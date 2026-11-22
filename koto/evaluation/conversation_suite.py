"""Koto conversational regression suite (1.3.0 brief, Phase 7).

The prompts are exactly the ones listed in the 1.3.0 brief, grouped into its six
categories. The application-layer rules that recognise disagreement, repair,
topic change and some emotions were written after reading this list, so for the
Python *release* pipeline this suite is a specification check, not an
independent measurement; ``behaviour_suite`` remains the independent one. For
the raw model (``raw`` pipeline, llama.cpp, Ollama) it is a fair test because
the prompts are removed from training data by ``scripts/build_mix.py``.

Case format and scoring: :mod:`koto.evaluation.behaviour_suite`.
"""

from __future__ import annotations

from typing import List

from hibari.inference.tasks import parse_task_request
from koto.evaluation.behaviour_suite import BCase
from koto.evaluation.upgrade_suite import Check

GREET = r"\b(hi|hello|hey)\b"
ASKS_FOR_TEXT = r"\b(share|send|paste|give|type|provide|which|what)\b.*\b(text|sentence|message|it)\b|\bwhat would you like\b"

CASES: List[BCase] = [
    # ── Natural conversation (one conversation, every turn scored) ──
    BCase("N1", "natural", ["hi", "how are you?", "what are you doing?", "that's interesting.", "tell me more."],
          "Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; "
          "continues on 'tell me more' instead of changing topic.",
          {0: Check(require_any=[GREET + r"|\?"], max_words=25),
           1: Check(require_any=[r"\b(good|well|fine|great|thanks|thank)\b"], max_words=35),
           2: Check(require_any=[r"\b(chat\w*|talk\w*|here|nothing much|not much|just|help\w*|listen\w*)\b"],
                    forbid=[r"^\W*i'?m (doing )?(well|good|fine)\b"], max_words=40),
           3: Check(require_any=[r"\?", r"\b(glad|yes|right|really|isn'?t it|thanks|indeed|agree|fun|cool)\b"], max_words=40),
           4: Check(min_words=4, max_words=70, forbid=[r"\bwhat would you like to talk about\b"])}),
    # ── Empathy ──
    BCase("E1", "empathy", ["I feel like nobody understands me."], "Acknowledges the loneliness; invites to talk.",
          {0: Check(max_words=70)}, affect={0: "empathy"}),
    BCase("E2", "empathy", ["I had a difficult day."], "Acknowledges the day; asks what happened (about the USER, not 'them').",
          {0: Check(max_words=60, forbid=[r"\bfor them\b", r"\bsomeone (close to you|you care about)\b"])}, affect={0: "empathy"}),
    BCase("E3", "empathy", ["I'm disappointed with myself."], "Acknowledges; no 'you did great'; gentle question.",
          {0: Check(max_words=70)}, affect={0: "empathy"}),
    # ── Sympathy ──
    BCase("Y1", "sympathy", ["I lost something important today."], "Sympathy; asks what was lost; not condolences for a death.",
          {0: Check(max_words=60, forbid=[r"\bcondolences\b", r"\brest in peace\b"])}, affect={0: "empathy"}),
    BCase("Y2", "sympathy", ["My friend is going through a difficult time."], "Sympathy for the friend (and the user).",
          {0: Check(max_words=70)}, affect={0: "empathy"}),
    # ── Context continuity ──
    BCase("C1", "context", ["My name is Alex.", "I am studying computer science.", "I enjoy programming.",
                            "What do you remember about my interests?"],
          "Recalls computer science and/or programming (and may use the name Alex).",
          {3: Check(require_any=[r"\bprogramm\w*", r"\bcomputer science\b", r"\bcoding\b"], max_words=60, allow_intro=True)}),
    # ── Reformulation ──
    BCase("R1", "reformulation", ["i dont know what to do now"],
          "Chat, not a correction: responds to the feeling and asks what is going on.",
          {0: Check(forbid=[r"^\W*i don'?t know what to do now\W*$", r"\bcorrect(ed)? (version|sentence)\b", r"\bgrammar\b"],
                    max_words=60)}, affect={0: "empathy"}),
    BCase("R2", "reformulation", ["can u make this sentence better"], "No sentence given: asks for it.",
          {0: Check(require_any=[ASKS_FOR_TEXT], max_words=30)}),
    BCase("R3", "reformulation", ["rewrite this in a polite way"], "No text given: asks for it.",
          {0: Check(require_any=[ASKS_FOR_TEXT], max_words=30)}),
    BCase("R4", "reformulation", ["correct my grammar"], "No text given: asks for it.",
          {0: Check(require_any=[ASKS_FOR_TEXT], max_words=30)}),
    # ── Conversational naturalness ──
    BCase("T1", "naturalness", ["Is coffee bad for you?", "I disagree with you."],
          "Accepts the disagreement calmly, asks the user's view; no thanks, no hostility.",
          {1: Check(require_any=[r"\b(fair|point|i see|okay|that'?s fine|might be right|why|what do you think|understand|"
                                 r"opinion|view|depends|different)\b"],
                    forbid=[r"\byou'?re welcome\b", r"\bglad i could help\b", r"\bstupid\b"], max_words=60)}),
    BCase("T2", "naturalness", ["Can you suggest a movie?", "That's not what I meant."],
          "Apologises / asks what the user meant.",
          {1: Check(require_any=[r"\b(sorry|my mistake|what did you mean|what do you mean|could you (explain|clarify|tell)|"
                                 r"can you (explain|clarify|tell)|let me try)\b"], max_words=45)}),
    BCase("T3", "naturalness", ["I think reading before bed helps me sleep.", "Why do you think so?"],
          "Gives a reason (or asks for the user's view); does not ignore the question.",
          {1: Check(require_any=[r"\b(because|since|helps?|relax\w*|calm\w*|screen|mind|might|maybe|could)\b"], max_words=70)}),
    BCase("T4", "naturalness", ["I love cricket.", "Anyway, let's talk about something else."],
          "Accepts the topic change and offers / asks for a new topic; does not continue cricket.",
          {1: Check(require_any=[r"\b(sure|okay|ok|of course|alright|what would you like|what do you want|what'?s on your mind|"
                                 r"anything)\b"], forbid=[r"\bcricket\b"], max_words=40)}),
]

CATEGORY_ORDER = ["natural", "empathy", "sympathy", "context", "reformulation", "naturalness"]


def eval_user_texts() -> List[str]:
    out: List[str] = []
    for c in CASES:
        for t in c.turns:
            out.append(t)
            req = parse_task_request(t)
            if req and req.text:
                out.append(req.text)
    return out
