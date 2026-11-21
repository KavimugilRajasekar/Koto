"""Koto 1.1.0 evaluation suite: conversation, context, rephrasing and grammar.

Categories (from the 1.1.0 brief): A basic conversation, B contextual
conversation, C rephrasing, D formal rephrasing, E casual rephrasing,
F grammar correction, G meaning preservation, H robustness, plus S — the
behaviour examples given in sections 2 and 3 of the brief, used as extra
held-out probes.

How a case runs
* ``turns`` are user messages sent one after another in ONE session; the
  model's own replies stay in the history (context tests depend on them).
* ``checks`` maps a 0-based user-turn index to a :class:`Check`; only those
  turns are scored. A case passes only if every scored turn passes every check.

Scoring is rule-based and automatic (regular expressions, protected-term
preservation, length ratios, repetition, echo, self-introduction and lead
detection). A chrF-style similarity to a hand-written reference is recorded
for rewrites but never decides pass/fail on its own. Grammar-correction
cases (F) require one of the exact correct sentences.

Prompts for F are sent as ``Correct grammar: "<sentence>"`` because the brief
lists only the sentences; every other prompt is used exactly as written in
the brief.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from hibari.evaluation.metrics import (
    ai_disclaimer,
    char_ngram_f,
    echo_ratio,
    grammar_heuristic,
    has_lead,
    length_ratio,
    ngram_repetition,
    repeated_sentence,
    self_introduction,
    words,
)
from hibari.inference.tasks import missing_protected_terms, parse_task_request
from koto.data.tasks import new_content_words


@dataclass
class Check:
    kind: str = "chat"                    # "chat" or "rewrite"
    require: List[str] = field(default_factory=list)       # every regex must match (case-insensitive)
    require_any: List[str] = field(default_factory=list)   # at least one must match
    forbid: List[str] = field(default_factory=list)        # none may match (case-insensitive)
    forbid_cs: List[str] = field(default_factory=list)     # none may match (case-sensitive)
    full: List[str] = field(default_factory=list)          # output must fully match one (case-insensitive)
    min_words: int = 1
    max_words: int = 120
    source: Optional[str] = None          # text being rewritten
    reference: Optional[str] = None       # hand-written reference rewrite (similarity only)
    must_differ: bool = False             # rewrite must change the source
    min_source_similarity: float = 0.0    # chrF to the source (already-correct input)
    length_ratio: Tuple[float, float] = (0.0, 99.0)
    max_new_content_words: Optional[int] = None
    allow_intro: bool = False


@dataclass
class Case:
    id: str
    category: str
    turns: List[str]
    expected: str
    checks: Dict[int, Check]


def _rw(source: str, reference: str, **kw) -> Check:
    kw.setdefault("length_ratio", (0.4, 2.2))
    return Check(kind="rewrite", source=source, reference=reference, **kw)


GREET = r"\b(hi|hello|hey|good (morning|evening|afternoon))\b"
WELL = r"\b(good|well|fine|great|thanks|thank)\b"

LONG_PARAGRAPH = (
    "yesterday me and my team was working on the new website for the library. we fixed 12 bugs and added a "
    "search page, but the login page is still slow and some users cant reset there password. the manager want "
    "us to finish everything before Friday, so tomorrow we will test it on Android and Windows and then send "
    "the report to Mr. Rao."
)
TECH_SENTENCE = "Our API returns HTTP 404 errors for 3% of requests after upgrading to Node.js v18.2!"

CASES: List[Case] = [
    # ── A. Basic conversation ──
    Case("A1", "basic", ["Hello!"], "A friendly greeting, optionally asking how the user is.",
         {0: Check(require_any=[GREET], max_words=30)}),
    Case("A2", "basic", ["How are you doing today?"], "Says how it is doing and asks back.",
         {0: Check(require_any=[WELL], max_words=35)}),
    Case("A3", "basic", ["What can you do?"], "Briefly lists what it can help with.",
         {0: Check(require_any=[r"\b(chat|talk|help|questions?|rephras\w*|rewrit\w*|grammar|answer)\b"], max_words=60)}),
    Case("A4", "basic", ["Tell me something interesting."], "Shares one interesting, true fact.",
         {0: Check(min_words=8, max_words=60, forbid=[r"^\W*(what|which|why)\b.*\?\s*$", r"\bnot sure\b", r"\bwhat you are talking\b",
                                                    r"\bi don'?t know\b", r"\bsorry\b"])}),
    Case("A5", "basic", ["Thank you for helping me."], "Accepts the thanks naturally.",
         {0: Check(require_any=[r"\b(welcome|anytime|glad|pleasure|happy to help|no problem)\b"], max_words=30)}),
    Case("A6", "basic", ["What should I learn next if I want to become a software developer?"],
         "Concrete next steps (a language, data structures, Git, projects).",
         {0: Check(require_any=[r"\b(programming|python|javascript|java|data structures?|algorithms?|git|web|projects?|languages?)\b"],
                   min_words=10, max_words=90)}),
    # ── B. Contextual conversation (model's own replies kept) ──
    Case("B1", "context", ["I am learning Python.", "What should I learn after that?", "Can you give me a simple project idea?"],
         "Turn 2 names what to learn after Python; turn 3 suggests a small project.",
         {1: Check(require_any=[r"\b(django|flask|pandas|numpy|librar\w*|oop|object|data|web|sql|git|frameworks?|functions|classes|modules)\b"],
                   forbid=[r"\bafter what\b", r"\bwhat do you mean\b"], max_words=90),
          2: Check(require_any=[r"\b(build|make|create|write|project|app|game|script|calculator|to-?do|bot|tracker|program)\b"], max_words=90)}),
    Case("B2", "context", ["I want to build a mobile application.", "I am planning to use Flutter.",
                           "Which programming language should I learn for it?"],
         "Answers Dart, because Flutter apps are written in Dart.",
         {2: Check(require=[r"\bdart\b"], max_words=80)}),
    Case("B3", "context", ["I have an exam tomorrow.", "I haven't prepared properly.", "What should I do now?"],
         "Practical last-minute exam advice that uses the earlier turns.",
         {2: Check(require_any=[r"\b(review|revise|revision|study|focus|important|topics|notes|sleep|rest|practi[cs]e|past papers?)\w*"],
                   forbid=[r"\bcongrat"], max_words=90)}),
    # ── C. Sentence rephrasing ──
    Case("C1", "rephrase", ['Rephrase: "i am learning programming from two years."'],
         "I have been learning programming for two years.",
         {0: _rw("i am learning programming from two years.", "I have been learning programming for two years.",
                 require=[r"\bfor two years\b", r"\bprogramming\b"],
                 require_any=[r"\b(have|i've) been learning\b", r"\bhave (learned|learnt)\b"],
                 forbid=[r"\bfrom two years\b"], must_differ=True)}),
    Case("C2", "rephrase", ['Rephrase: "he don\'t know how to use this application."'],
         "He doesn't know how to use this application.",
         {0: _rw("he don't know how to use this application.", "He doesn't know how to use this application.",
                 require=[r"\bdoes(n't| not) know\b", r"\b(application|app)\b"], forbid=[r"\bhe don'?t\b"], must_differ=True)}),
    Case("C3", "rephrase", ['Rephrase: "today i completed my project and submitted it to my mentor."'],
         "Today, I completed my project and submitted it to my mentor.",
         {0: _rw("today i completed my project and submitted it to my mentor.",
                 "Today, I completed my project and submitted it to my mentor.",
                 require=[r"\bproject\b", r"\bmentor\b", r"\b(completed|finished)\b", r"\b(submitted|sent|gave|handed)\b"],
                 forbid_cs=[r"(?<![A-Za-z])i(?![A-Za-z'])"], must_differ=True)}),
    Case("C4", "rephrase", ['Rephrase: "the application is working but there is some issue in login page."'],
         "The application is working, but there is an issue with the login page.",
         {0: _rw("the application is working but there is some issue in login page.",
                 "The application is working, but there is an issue with the login page.",
                 require=[r"\blogin\b", r"\b(working|works)\b"], require_any=[r"\b(issue|problem|bug)\b"],
                 forbid=[r"\bin login page\b"], must_differ=True)}),
    Case("C5", "rephrase", ['Rephrase: "we are planning to develop a new software for our college."'],
         "We are planning to develop new software for our college.",
         {0: _rw("we are planning to develop a new software for our college.",
                 "We are planning to develop new software for our college.",
                 require=[r"\bcollege\b", r"\bsoftware\b", r"\b(plan|planning)\b"], forbid=[r"\ba new software\b"], must_differ=True)}),
    # ── D. Formal rephrasing ──
    Case("D1", "formal", ['Make this professional: "I need leave tomorrow because I have some personal work."'],
         "A formal leave request for tomorrow citing a personal matter.",
         {0: _rw("I need leave tomorrow because I have some personal work.",
                 "I would like to request leave tomorrow due to a personal matter.",
                 require=[r"\bleave\b", r"\btomorrow\b"], require_any=[r"\b(would like|request|kindly|unable|please|may i)\b"],
                 forbid=[r"\b(gonna|wanna|u|ur|pls)\b"], must_differ=True)}),
    Case("D2", "formal", ['Make this professional: "I want to know whether my application got selected."'],
         "I would like to know whether my application has been selected.",
         {0: _rw("I want to know whether my application got selected.",
                 "I would like to know whether my application has been selected.",
                 require=[r"\bapplication\b", r"\b(selected|accepted|status|successful|shortlisted)\b"],
                 require_any=[r"\b(would like|could you|kindly|please|inquire|enquire|may i)\b"],
                 forbid=[r"\bgot selected\b"], must_differ=True)}),
    Case("D3", "formal", ['Make this professional: "I have finished the work and waiting for your reply."'],
         "I have completed the work and look forward to your reply.",
         {0: _rw("I have finished the work and waiting for your reply.",
                 "I have completed the work and look forward to your reply.",
                 require_any=[r"\b(finished|completed)\b"], require=[r"\b(reply|response|feedback)\b"],
                 forbid=[r"\band waiting\b"], must_differ=True)}),
    Case("D4", "formal", ['Make this professional: "Can you send me the details as soon as possible?"'],
         "Could you please send me the details at your earliest convenience?",
         {0: _rw("Can you send me the details as soon as possible?",
                 "Could you please send me the details at your earliest convenience?",
                 require=[r"\bdetails\b"], require_any=[r"\b(could you|would you|kindly|please|i would)\b"], must_differ=True)}),
    # ── E. Casual rephrasing ──
    Case("E1", "casual", ['Make this casual: "I would appreciate it if you could assist me with this task."'],
         "Could you help me with this?",
         {0: _rw("I would appreciate it if you could assist me with this task.", "Could you help me with this?",
                 require_any=[r"\b(help|hand)\b"], forbid=[r"\bi would appreciate it\b", r"\bassist\b"], must_differ=True,
                 length_ratio=(0.2, 1.5))}),
    Case("E2", "casual", ['Make this casual: "I am currently occupied with some important work."'],
         "I'm busy with some important work right now.",
         {0: _rw("I am currently occupied with some important work.", "I'm busy with some important work right now.",
                 require_any=[r"\b(busy|tied up|swamped|working on)\b"], forbid=[r"\boccupied\b"], must_differ=True,
                 length_ratio=(0.3, 1.6))}),
    Case("E3", "casual", ['Make this casual: "I will contact you once the implementation is completed."'],
         "I'll get back to you once it's done.",
         {0: _rw("I will contact you once the implementation is completed.", "I'll get back to you once it's done.",
                 require_any=[r"\b(get back|reach out|let you know|text|call|ping|message|contact|hit you up)\b"],
                 require=[r"\b(done|finished|complete\w*|ready|once|when)\b"],
                 forbid=[r"\bonce the implementation is completed\b", r"\bcontact you for\b"], must_differ=True,
                 length_ratio=(0.3, 1.6))}),
    # ── F. Grammar correction (exact corrections) ──
    Case("F1", "grammar", ['Correct grammar: "She go to school every day."'], "She goes to school every day.",
         {0: _rw("She go to school every day.", "She goes to school every day.", full=[r"she goes to school every day\.?"])}),
    Case("F2", "grammar", ['Correct grammar: "They was playing football yesterday."'], "They were playing football yesterday.",
         {0: _rw("They was playing football yesterday.", "They were playing football yesterday.",
                 full=[r"they were playing football yesterday\.?"])}),
    Case("F3", "grammar", ['Correct grammar: "I has completed my assignment."'], "I have completed my assignment.",
         {0: _rw("I has completed my assignment.", "I have completed my assignment.", full=[r"i have completed my assignment\.?"])}),
    Case("F4", "grammar", ['Correct grammar: "He is working in this project since Monday."'],
         "He has been working on this project since Monday.",
         {0: _rw("He is working in this project since Monday.", "He has been working on this project since Monday.",
                 full=[r"he has been working on this project since monday\.?"])}),
    Case("F5", "grammar", ['Correct grammar: "We doesn\'t have enough time."'], "We don't have enough time.",
         {0: _rw("We doesn't have enough time.", "We don't have enough time.",
                 full=[r"we (don't|do not) have enough time\.?"])}),
    # ── G. Meaning preservation ──
    Case("G1", "preservation", ['Rephrase: "The meeting is scheduled for Monday at 10 AM."'],
         "Same meeting, Monday, 10 AM; nothing added or changed.",
         {0: _rw("The meeting is scheduled for Monday at 10 AM.", "The meeting is set for Monday at 10 AM.",
                 require=[r"\bmeeting\b", r"\bmonday\b", r"\b10\s*(am|a\.m\.)"],
                 forbid=[r"\b(tuesday|wednesday|thursday|friday|saturday|sunday)\b", r"\bpm\b"])}),
    Case("G2", "preservation", ['Rephrase: "The project contains three modules and five test cases."'],
         "Three modules and five test cases are kept.",
         {0: _rw("The project contains three modules and five test cases.",
                 "There are three modules and five test cases in the project.",
                 require=[r"\b(three|3) modules\b", r"\b(five|5) test(s| cases)\b", r"\bproject\b"])}),
    Case("G3", "preservation", ['Rephrase: "My application supports Android but not iOS."'],
         "Android supported, iOS not supported.",
         {0: _rw("My application supports Android but not iOS.", "My application works on Android, but not on iOS.",
                 require=[r"\bandroid\b", r"\bios\b"], require_any=[r"\bnot\b", r"n't\b", r"\bonly\b"],
                 forbid=[r"\b(both|android and ios)\b"])}),
    # ── H. Robustness ──
    Case("H1", "robustness", ['Rephrase: "This sentence is already correct."'],
         "Keeps the sentence (or makes only a small improvement); adds nothing.",
         {0: _rw("This sentence is already correct.", "This sentence is already correct.",
                 require=[r"\bsentence\b", r"\bcorrect\b"], min_source_similarity=0.6, length_ratio=(0.5, 1.5))}),
    Case("H2", "robustness", ['Rephrase: ""'], "Asks for the text to rephrase.",
         {0: Check(require_any=[r"\b(share|provide|give|send|type|enter|paste)\b"], require=[r"\b(text|sentence|message)\b"],
                   max_words=25)}),
    Case("H3", "robustness", ['Rephrase: "I."'], "Does not invent details for a one-word fragment.",
         {0: _rw("I.", "I.", max_words=4, length_ratio=(0.0, 4.0), max_new_content_words=1)}),
    Case("H4", "robustness", [f'Rephrase: "{LONG_PARAGRAPH}"'],
         "Rewrites the paragraph correctly, keeping 12 bugs, Friday, Android, Windows and Mr. Rao.",
         {0: _rw(LONG_PARAGRAPH, None, length_ratio=(0.5, 1.6), max_words=160, require=[r"\b12\b", r"\bfriday\b", r"\bandroid\b",
                 r"\bwindows\b", r"\brao\b"], must_differ=True)}),
    Case("H5", "robustness", [f'Rephrase: "{TECH_SENTENCE}"'],
         "Keeps API, HTTP 404, 3%, Node.js and v18.2 exactly.",
         {0: _rw(TECH_SENTENCE, "After upgrading to Node.js v18.2, our API returns HTTP 404 errors for 3% of requests.",
                 require=[r"\bapi\b", r"\bhttp\b", r"\b404\b", r"\b3\s?%", r"node\.?js", r"v?18\.2\b"])}),
    Case("H6", "robustness", ['Rephrase: "i goes to the market daily."', "What is the capital of Japan?"],
         "Turn 2 is answered as a normal question (Tokyo), not rewritten.",
         {1: Check(require=[r"\btokyo\b"], forbid=[r"\bmarket\b", r"^\s*task:", r"\binput:"], max_words=40)}),
    Case("H7", "robustness", ['Rephrase: "he left it there after they came"'],
         "Rewrites without adding who/what/where details that are not in the text.",
         {0: _rw("he left it there after they came", "He left it there after they came.",
                 require=[r"\bleft\b", r"\b(there|that place)\b", r"\b(came|arrived)\b"],
                 max_new_content_words=1, length_ratio=(0.5, 1.8))}),
    # ── S. Behaviour examples from the brief (held-out probes) ──
    Case("S1", "spec_examples", ["Hello! How are you?"], "I'm doing well, thanks for asking! How are you doing today?",
         {0: Check(require_any=[WELL], max_words=35)}),
    Case("S2", "spec_examples", ["What is Python?"], "Python is a programming language known for simple, readable syntax.",
         {0: Check(require=[r"\bprogramming language\b"], max_words=70)}),
    Case("S3", "spec_examples", ["I am feeling tired today."], "Empathy plus a small suggestion such as taking a break.",
         {0: Check(require_any=[r"\b(rest|break|sleep|tired|tiring|long day|recharge|relax)\w*"], max_words=50)}),
    Case("S4", "spec_examples", ['Rephrase this sentence: "i am go to college yesterday and meet my friends"'],
         "I went to college yesterday and met my friends.",
         {0: _rw("i am go to college yesterday and meet my friends", "I went to college yesterday and met my friends.",
                 require=[r"\bwent to college yesterday\b", r"\bmet my friends\b"])}),
    Case("S5", "spec_examples", ['Rephrase this sentence: "The project was completed by me and it is working good."'],
         "I completed the project, and it is working well.",
         {0: _rw("The project was completed by me and it is working good.", "I completed the project, and it is working well.",
                 require=[r"\bi completed the project\b", r"\bworking well\b"])}),
    Case("S6", "spec_examples", ['Make this sentence more professional: "I can\'t come today because I have some work."'],
         "I am unable to attend today due to some personal work.",
         {0: _rw("I can't come today because I have some work.", "I am unable to attend today due to some personal work.",
                 require=[r"\btoday\b"], require_any=[r"\b(unable|not be able|cannot|regret|will not be able)\b"], must_differ=True)}),
    Case("S7", "spec_examples", ['Make this sentence shorter: "Due to the fact that I was not feeling well, I decided not to attend the meeting."'],
         "I skipped the meeting because I wasn't feeling well.",
         {0: _rw("Due to the fact that I was not feeling well, I decided not to attend the meeting.",
                 "I skipped the meeting because I wasn't feeling well.",
                 require=[r"\bmeeting\b"], require_any=[r"\b(not feeling well|wasn't feeling well|unwell|sick|ill)\b"],
                 length_ratio=(0.3, 0.85))}),
]

CATEGORY_ORDER = ["basic", "context", "rephrase", "formal", "casual", "grammar", "preservation", "robustness", "spec_examples"]


def eval_user_texts() -> List[str]:
    """Every user message and every rewrite source in the suite (for leak checks)."""
    out: List[str] = []
    for c in CASES:
        for t in c.turns:
            out.append(t)
            req = parse_task_request(t)
            if req and req.text:
                out.append(req.text)
        for chk in c.checks.values():
            if chk.source:
                out.append(chk.source)
    return out


def score_turn(check: Check, output: str, prompt: str, stopped_on_eos: bool = True) -> Dict:
    low = output.strip().lower()
    res: Dict[str, object] = {}
    res["non_empty"] = bool(low)
    for p in check.require:
        res[f"require:{p}"] = bool(re.search(p, low))
    if check.require_any:
        res["require_any"] = any(re.search(p, low) for p in check.require_any)
    for p in check.forbid:
        res[f"forbid:{p}"] = not re.search(p, low)
    for p in check.forbid_cs:
        res[f"forbid_cs:{p}"] = not re.search(p, output)
    if check.full:
        res["exact_correction"] = any(re.fullmatch(p, low) for p in check.full)
    n = len(words(output))
    res["length_words"] = check.min_words <= n <= check.max_words
    res["no_repetition"] = ngram_repetition(output) <= 0.2 and not repeated_sentence(output)
    res["no_ai_disclaimer"] = not ai_disclaimer(output)
    res["complete"] = stopped_on_eos
    if check.kind == "chat":
        res["no_echo"] = echo_ratio(output, prompt) < 0.5
        if not check.allow_intro:
            res["no_self_intro"] = not self_introduction(output)
    else:
        src = check.source or ""
        res["output_only"] = not has_lead(output) and not re.search(r"^\s*task:|\binput:", low)
        if src:
            res["preserves_terms"] = not missing_protected_terms(src, output)
            lo, hi = check.length_ratio
            res["length_ratio"] = lo <= length_ratio(output, src) <= hi
            if check.must_differ:
                # any edit counts (capitalisation and punctuation fixes are changes);
                # whether the edit is correct is decided by the other checks
                res["changed"] = re.sub(r"\s+", " ", output.strip()) != re.sub(r"\s+", " ", src.strip())
            if check.min_source_similarity:
                res["close_to_source"] = char_ngram_f(output, src) >= check.min_source_similarity
            g = grammar_heuristic(output)
            res["capitalised"] = g["capitalised"]
            res["terminal_punctuation"] = g["terminal_punctuation"]
        if check.max_new_content_words is not None:
            res["no_invented_content"] = len(new_content_words(output, src)) <= check.max_new_content_words
    passed = all(v for v in res.values() if isinstance(v, bool))
    info = {
        "missing_terms": missing_protected_terms(check.source, output) if check.source else [],
        "reference_chrf": round(char_ngram_f(output, check.reference), 3) if check.reference else None,
        "echo_ratio": round(echo_ratio(output, prompt), 3),
        "repetition_3gram": round(ngram_repetition(output), 3),
        "grammar_heuristic_ok": all(grammar_heuristic(output).values()),
    }
    return {"passed": passed, "checks": res, "failed_checks": [k for k, v in res.items() if v is False], **info}
