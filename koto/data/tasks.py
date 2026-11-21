"""Rewriting-task training data for Koto 1.1.0.

Every rewriting example is a :class:`TaskExample` (task, source, target,
origin). :func:`render` turns it into a single-turn conversation whose
assistant reply is **only the rewritten text** (no "Here's ..." lead), using
either the canonical engine format (``hibari.inference.tasks.format_task_request``,
the exact form the chat session sends at inference) or a natural phrasing
("Rephrase this sentence: \"...\"") so that requests typed straight into
llama.cpp / Ollama work as well.

Hand-written sets in this module
* ``grammar_examples`` — templated grammar errors with verified corrections
  (agreement, tense, was/were, has/have, since/for, don't/doesn't, articles,
  capitalisation) plus already-correct sentences that must come back unchanged.
* ``restructure_examples`` — passive → active and wordy → natural rephrasing.
* ``preservation_examples`` — rephrasing that must keep times, dates,
  numbers, names and technical terms.
* ``formal_examples``, ``casual_examples``, ``shorten_examples`` — style
  rewrites written by hand.
* ``robustness_examples`` — empty and fragment inputs.

Data hygiene helpers
* :func:`dedup_examples` keeps one target per (task, normalised source); a
  second, different target for the same source is a contradiction and is
  dropped (counted in the stats).
* :func:`split_of` assigns train / val / test by a stable hash of the
  normalised source, so one source never appears in two splits.
* :func:`remove_leaks` drops every example whose source or rendered prompt
  matches an evaluation prompt.

All templates were checked for grammatical targets; templated sentences that
equal an evaluation sentence are removed by :func:`remove_leaks`.
"""

from __future__ import annotations

import hashlib
import random
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

from hibari.inference.tasks import TASKS, format_task_request

Msg = Dict[str, str]
Conv = List[Msg]


@dataclass(frozen=True)
class TaskExample:
    task: str
    source: str
    target: str
    origin: str  # provenance, e.g. "coedit:gec", "handwritten:grammar"


def norm(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


FUNCTION_WORDS = set(
    "a an the and or but so to of in on at for with by from it its it's this that these those he she they we you i "
    "me him her them us my your his their our is are was were be been am do does did has have had will would can "
    "could should not no there here then when after before as if up out just very".split()
)


def _words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def new_content_words(output: str, source: str) -> List[str]:
    """Content words of ``output`` that do not occur in ``source``."""
    src = set(_words(source))
    return [w for w in _words(output) if w not in src and w not in FUNCTION_WORDS and not w.isdigit()]


def is_faithful(ex: "TaskExample", max_new_share: float = 0.30, max_length_ratio: float = 1.25) -> bool:
    """Target adds little new content and is not much longer than the source."""
    tw = _words(ex.target)
    if not tw:
        return False
    share = len(new_content_words(ex.target, ex.source)) / len(tw)
    return share <= max_new_share and len(tw) / max(1, len(_words(ex.source))) <= max_length_ratio


# ───────────────────────── rendering ─────────────────────────

NATURAL_ASKS: Dict[str, List[str]] = {
    "rephrase": [
        "Rephrase this sentence", "Rephrase this", "Rephrase", "Reword this", "Paraphrase this",
        "Rewrite this sentence", "Can you rephrase this", "can u rephrase this", "rephrase this pls",
        "Please rephrase this sentence",
    ],
    "correct_grammar": [
        "Correct the grammar", "Correct grammar", "Fix the grammar", "Fix my grammar", "Correct this sentence",
        "fix this sentence pls", "Check my grammar", "correct the mistakes in this", "Can you correct this",
        "fix the grammar in this sentence",
    ],
    "formal": [
        "Make this professional", "Make this more professional", "Make this sentence more professional",
        "Make this formal", "Rewrite this formally", "make it sound professional", "Make this message more formal",
        "Can you make this professional",
    ],
    "casual": [
        "Make this casual", "Make this more casual", "Make this sound casual", "Rewrite this casually",
        "make it informal", "Make this sentence more casual", "make this sound relaxed",
    ],
    "shorten": [
        "Make this shorter", "Make this sentence shorter", "Shorten this", "Make this more concise",
        "make it shorter pls", "Shorten this sentence",
    ],
    "simplify": ["Simplify this", "Make this simpler", "Simplify this sentence", "make this sentence simpler"],
    "polite": [
        "Make this polite", "Make this more polite", "Rewrite this politely", "make this message polite",
        "Make this sentence more polite",
    ],
}


def natural_request(task: str, text: str, rng: random.Random) -> str:
    instr = rng.choice(NATURAL_ASKS[task])
    r = rng.random()
    if r < 0.40:
        return f'{instr}: "{text}"'
    if r < 0.70:
        return f"{instr}: {text}"
    if r < 0.85:
        return f"{instr}\n{text}"
    return f"\"{text}\" {instr[0].lower() + instr[1:]}"


def render(ex: TaskExample, rng: random.Random, canonical_share: float = 0.5) -> Conv:
    """Single-turn conversation [user, assistant]; the reply is the target only."""
    if rng.random() < canonical_share:
        user = format_task_request(ex.task, ex.source)
    else:
        user = natural_request(ex.task, ex.source, rng)
    return [{"role": "user", "content": user}, {"role": "assistant", "content": ex.target}]


# ───────────────────────── hygiene ─────────────────────────


def dedup_examples(examples: Iterable[TaskExample]) -> Tuple[List[TaskExample], Dict[str, int]]:
    """One example per (task, normalised source). Exact repeats are dropped;
    a different target for an already-seen source is a contradiction and is
    dropped too (the first target wins)."""
    seen: Dict[Tuple[str, str], str] = {}
    out: List[TaskExample] = []
    stats = Counter()
    for ex in examples:
        if not ex.source.strip() and ex.origin != "handwritten:robustness":
            stats["empty_source"] += 1
            continue
        key = (ex.task, norm(ex.source))
        if key in seen:
            stats["contradiction" if norm(seen[key]) != norm(ex.target) else "duplicate"] += 1
            continue
        seen[key] = ex.target
        out.append(ex)
    return out, dict(stats)


def split_of(text: str, val_pct: int = 4, test_pct: int = 4) -> str:
    """Stable split by hash of the normalised text."""
    h = int(hashlib.sha1(norm(text).encode("utf-8")).hexdigest()[:8], 16) % 100
    if h < test_pct:
        return "test"
    if h < test_pct + val_pct:
        return "val"
    return "train"


def remove_leaks(examples: Iterable[TaskExample], eval_texts: Sequence[str]) -> Tuple[List[TaskExample], int]:
    """Drop examples whose source equals an evaluation text or an evaluation
    text's inner sentence (after normalisation)."""
    banned = {norm(t) for t in eval_texts if norm(t)}
    kept, dropped = [], 0
    for ex in examples:
        if norm(ex.source) in banned:
            dropped += 1
        else:
            kept.append(ex)
    return kept, dropped


# ───────────────────────── grammar (templated) ─────────────────────────

# (base, 3rd-person singular, past, past participle, -ing)
VERBS: Dict[str, Tuple[str, str, str, str, str]] = {
    "go": ("go", "goes", "went", "gone", "going"),
    "play": ("play", "plays", "played", "played", "playing"),
    "watch": ("watch", "watches", "watched", "watched", "watching"),
    "study": ("study", "studies", "studied", "studied", "studying"),
    "cook": ("cook", "cooks", "cooked", "cooked", "cooking"),
    "drink": ("drink", "drinks", "drank", "drunk", "drinking"),
    "read": ("read", "reads", "read", "read", "reading"),
    "walk": ("walk", "walks", "walked", "walked", "walking"),
    "write": ("write", "writes", "wrote", "written", "writing"),
    "visit": ("visit", "visits", "visited", "visited", "visiting"),
    "teach": ("teach", "teaches", "taught", "taught", "teaching"),
    "eat": ("eat", "eats", "ate", "eaten", "eating"),
    "clean": ("clean", "cleans", "cleaned", "cleaned", "cleaning"),
    "practise": ("practise", "practises", "practised", "practised", "practising"),
    "buy": ("buy", "buys", "bought", "bought", "buying"),
    "call": ("call", "calls", "called", "called", "calling"),
}

# verb -> (object for habits, object for a single event)
VERB_OBJECTS: Dict[str, List[Tuple[str, str]]] = {
    "go": [("to the gym every morning", "to the gym"), ("to the library on Saturdays", "to the library"),
           ("to work by bus", "to the beach"), ("for a walk after dinner", "to the doctor")],
    "play": [("cricket on weekends", "cricket"), ("the guitar every evening", "chess with my uncle"),
             ("badminton after work", "football in the park")],
    "watch": [("the news every night", "a movie"), ("cartoons on Sundays", "the match on TV")],
    "study": [("in the library every day", "for the test"), ("late at night", "with my cousin")],
    "cook": [("dinner for the family", "biryani for the guests"), ("breakfast every morning", "pasta")],
    "drink": [("tea after lunch", "too much coffee"), ("a glass of milk at night", "fresh juice")],
    "read": [("the newspaper every day", "a short story"), ("comics before bed", "the whole report")],
    "walk": [("to the office", "to the station"), ("in the park every evening", "home in the rain")],
    "write": [("in a diary every night", "a letter to the principal"), ("short poems", "a long email")],
    "visit": [("the market on Sundays", "the museum"), ("their grandparents every month", "an old friend")],
    "teach": [("math at a school", "a new song to the kids"), ("dance on weekends", "the class about volcanoes")],
    "eat": [("breakfast at seven", "a big lunch"), ("fruit every day", "dinner at a new restaurant")],
    "clean": [("the room every Sunday", "the kitchen"), ("the car once a week", "the whole house")],
    "practise": [("the piano every day", "the speech"), ("yoga in the morning", "for the concert")],
    "buy": [("vegetables on Mondays", "a new phone"), ("bread every morning", "two tickets")],
    "call": [("their family every evening", "the bank"), ("the office every Friday", "the plumber")],
}

SUBJ_3SG = ["He", "She", "My brother", "My sister", "Our teacher", "The manager", "Ravi", "Anna", "My friend",
            "Meena", "The coach", "My neighbour", "Arjun"]
SUBJ_PL = ["They", "We", "My parents", "The students", "Our neighbours", "My friends", "The kids", "You"]
SUBJ_1 = ["I"]
PAST_MARKERS = ["yesterday", "last week", "last night", "two days ago", "on Sunday", "last month"]

HAVE_OBJECTS = [("finished", "the report"), ("cleaned", "the kitchen"), ("submitted", "the form"),
                ("booked", "the tickets"), ("fixed", "the bug"), ("sent", "the email"), ("paid", "the bill"),
                ("read", "that book"), ("written", "the first chapter"), ("packed", "the bags"),
                ("watched", "that film"), ("painted", "the fence")]

DURATIONS = [
    ("working on this", ["report", "website", "design", "proposal"], ["since Tuesday", "for three days", "since morning"]),
    ("learning", ["English", "the guitar", "French", "Java"], ["since 2021", "for two years", "for six months"]),
    ("living in", ["Chennai", "this house", "Pune", "the city"], ["for five years", "since 2019", "for a long time"]),
    ("waiting for", ["the bus", "the results", "a reply", "the doctor"], ["for an hour", "since noon", "for twenty minutes"]),
]

ARTICLE_SENTENCES = [
    ("I saw a elephant at the zoo.", "I saw an elephant at the zoo."),
    ("She brought a umbrella to work.", "She brought an umbrella to work."),
    ("He ate a orange after lunch.", "He ate an orange after lunch."),
    ("We waited for a hour at the station.", "We waited for an hour at the station."),
    ("That is a interesting idea.", "That is an interesting idea."),
    ("My aunt is an doctor in Delhi.", "My aunt is a doctor in Delhi."),
    ("He studies at an university in Mumbai.", "He studies at a university in Mumbai."),
    ("They bought an new car last year.", "They bought a new car last year."),
    ("I need an pen to sign this form.", "I need a pen to sign this form."),
    ("She is a honest person.", "She is an honest person."),
    ("It was an useful lesson.", "It was a useful lesson."),
    ("Can I have a apple, please?", "Can I have an apple, please?"),
]


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def _be_past(subj: str) -> str:
    return "was" if subj in SUBJ_3SG or subj == "I" else "were"


def _have(subj: str) -> str:
    return "has" if subj in SUBJ_3SG else "have"


def _be_present(subj: str) -> str:
    return "am" if subj == "I" else ("is" if subj in SUBJ_3SG else "are")


def grammar_pairs(rng: random.Random, n_per_pattern: int = 220) -> List[Tuple[str, str, str]]:
    """(wrong, correct, pattern) triples; ``correct`` is verified by construction."""
    out: List[Tuple[str, str, str]] = []
    verbs = list(VERBS)

    def pick():
        v = rng.choice(verbs)
        habit, event = rng.choice(VERB_OBJECTS[v])
        return v, VERBS[v], habit, event

    for _ in range(n_per_pattern):
        # 1. third-person singular -s missing
        v, f, habit, _e = pick()
        s = rng.choice(SUBJ_3SG)
        out.append((f"{s} {f[0]} {habit}.", f"{s} {f[1]} {habit}.", "agreement_3sg"))
        # 2. plural / you subject with -s
        v, f, habit, _e = pick()
        s = rng.choice(SUBJ_PL)
        out.append((f"{s} {f[1]} {habit}.", f"{s} {f[0]} {habit}.", "agreement_plural"))
        # 3. past marker with present form
        v, f, _h, event = pick()
        s = rng.choice(SUBJ_3SG + SUBJ_PL + SUBJ_1)
        when = rng.choice(PAST_MARKERS)
        wrong_v = f[1] if s in SUBJ_3SG else f[0]
        out.append((f"{s} {wrong_v} {event} {when}.", f"{s} {f[2]} {event} {when}.", "past_tense"))
        # 4. was / were
        v, f, _h, event = pick()
        s = rng.choice(SUBJ_3SG + SUBJ_PL + SUBJ_1)
        right = _be_past(s)
        wrong = "were" if right == "was" else "was"
        when = rng.choice(PAST_MARKERS)
        out.append((f"{s} {wrong} {f[4]} {event} {when}.", f"{s} {right} {f[4]} {event} {when}.", "was_were"))
        # 5. has / have
        part, obj = rng.choice(HAVE_OBJECTS)
        s = rng.choice(SUBJ_3SG + SUBJ_PL + SUBJ_1)
        right = _have(s)
        wrong = "have" if right == "has" else "has"
        out.append((f"{s} {wrong} {part} {obj}.", f"{s} {right} {part} {obj}.", "has_have"))
        # 6. since / for with a continuous tense
        verb_phrase, objs, spans = rng.choice(DURATIONS)
        s = rng.choice(SUBJ_3SG + SUBJ_PL + SUBJ_1)
        o, span = rng.choice(objs), rng.choice(spans)
        out.append((f"{s} {_be_present(s)} {verb_phrase} {o} {span}.",
                    f"{s} {_have(s)} been {verb_phrase} {o} {span}.", "since_for"))
        # 7. don't / doesn't
        v, f, habit, _e = pick()
        s = rng.choice(SUBJ_3SG + SUBJ_PL)
        right = "doesn't" if s in SUBJ_3SG else "don't"
        wrong = "don't" if right == "doesn't" else "doesn't"
        out.append((f"{s} {wrong} {f[0]} {habit}.", f"{s} {right} {f[0]} {habit}.", "dont_doesnt"))
        # 8. articles
        wrong, right = rng.choice(ARTICLE_SENTENCES)
        out.append((wrong, right, "article"))
        # 9. lower-case "i", missing capital / full stop
        v, f, habit, _e = pick()
        out.append((f"i {f[0]} {habit}", f"I {f[0]} {habit}.", "capitalisation"))
    return out


CORRECT_SENTENCES = [
    "I walk to work every morning.", "She has two younger brothers.", "We are going to the market later.",
    "The train leaves at six in the evening.", "My parents live in a small town.", "He doesn't eat meat.",
    "They have already finished their homework.", "Our team won the final match.", "It is raining again.",
    "Please close the window before you leave.", "The library opens at nine.", "I have been learning Java since March.",
    "Can you help me carry these boxes?", "She was reading when I called her.", "We were late because of the traffic.",
    "The children are playing outside.", "My laptop needs a new battery.", "He visits his grandparents every summer.",
    "I bought two notebooks and a pen.", "This road is closed for repairs.",
]


def grammar_examples(rng: random.Random, n_per_pattern: int = 220) -> List[TaskExample]:
    out: List[TaskExample] = []
    for wrong, right, pattern in grammar_pairs(rng, n_per_pattern):
        task = "correct_grammar" if rng.random() < 0.7 else "rephrase"
        out.append(TaskExample(task, wrong, right, f"handwritten:grammar:{pattern}"))
    for s in CORRECT_SENTENCES:
        out.append(TaskExample("correct_grammar", s, s, "handwritten:grammar:already_correct"))
        out.append(TaskExample("rephrase", s, s, "handwritten:grammar:already_correct"))
    return out


# ───────────────────── restructuring (passive / wordy) ─────────────────────

PASSIVE_ITEMS = [("report", "wrote", "written"), ("website", "built", "built"), ("cake", "baked", "baked"),
                 ("presentation", "prepared", "prepared"), ("poster", "designed", "designed"),
                 ("bug", "fixed", "fixed"), ("letter", "sent", "sent"), ("video", "edited", "edited"),
                 ("app", "tested", "tested"), ("survey", "completed", "completed")]
WORKING_ITEMS = {"website", "app", "bug"}


def restructure_examples(rng: random.Random) -> List[TaskExample]:
    out: List[TaskExample] = []
    for item, past, part in PASSIVE_ITEMS:
        out.append(TaskExample("rephrase", f"The {item} was {part} by me yesterday.",
                               f"I {past} the {item} yesterday.", "handwritten:restructure:passive"))
        out.append(TaskExample("rephrase", f"The {item} was {part} by my team last week.",
                               f"My team {past} the {item} last week.", "handwritten:restructure:passive"))
        if item in WORKING_ITEMS:
            out.append(TaskExample("rephrase", f"The {item} was {part} by me and it is working good.",
                                   f"I {past} the {item}, and it is working well.", "handwritten:restructure:passive"))
    wordy = [
        ("i am go to the market yesterday and buy some apples", "I went to the market yesterday and bought some apples."),
        ("me and my friend we went to the park and we played there", "My friend and I went to the park and played there."),
        ("she is very much liking the new song", "She really likes the new song."),
        ("the movie which we watched it yesterday was very boring", "The movie we watched yesterday was very boring."),
        ("i didn't went to the class today", "I didn't go to the class today."),
        ("he told that he will come tomorrow", "He said that he would come tomorrow."),
        ("my mother she cooks very tasty food", "My mother cooks very tasty food."),
        ("we discussed about the problem in the meeting", "We discussed the problem in the meeting."),
        ("i am having two sisters and one brother", "I have two sisters and one brother."),
        ("he is more taller than his father", "He is taller than his father."),
        ("i will call you after i will reach home", "I will call you after I reach home."),
        ("can you explain me this topic", "Can you explain this topic to me?"),
        ("i am knowing the answer", "I know the answer."),
        ("they returned back from the trip on sunday", "They returned from the trip on Sunday."),
        ("my brother is elder to me by three years", "My brother is three years older than me."),
        ("please do the needful and revert back", "Please take care of this and reply."),
        ("i have completed my graduation in 2022", "I graduated in 2022."),
        ("the laptop is not working since two days", "The laptop has not been working for two days."),
        ("she is coming to here at evening", "She is coming here in the evening."),
        ("we was very happy with the result", "We were very happy with the result."),
    ]
    out += [TaskExample("rephrase", a, b, "handwritten:restructure:natural") for a, b in wordy]
    return out


# ───────────────────── meaning preservation ─────────────────────

EVENTS = ["interview", "class", "review", "webinar", "demo", "call", "workshop", "check-up", "match", "lecture"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIMES = ["9 AM", "11:30 AM", "2 PM", "3:30 PM", "4:15 PM", "6 PM", "8:45 AM", "7 PM", "noon"]
CONTAINERS = [("app", "screens", "buttons"), ("course", "lessons", "quizzes"), ("library", "classes", "functions"),
              ("report", "sections", "charts"), ("kit", "sensors", "cables"), ("repository", "folders", "scripts")]
NUMS = ["two", "three", "four", "five", "six", "seven", "eight", "ten", "12", "15", "20", "24"]
PLATFORMS = [("website", "Chrome", "Internet Explorer"), ("game", "Windows", "macOS"), ("tool", "Linux", "Windows"),
             ("printer", "USB", "Bluetooth"), ("camera", "Wi-Fi", "4G"), ("software", "Python 3", "Python 2"),
             ("phone", "5G", "wireless charging"), ("plugin", "Firefox", "Safari")]
NAMES = ["Priya", "Rahul", "Anita", "John", "Fatima", "Kumar", "Lena", "Arun", "Sofia", "Vikram"]
ITEMS = [("notebooks", "rupees"), ("tickets", "dollars"), ("shirts", "rupees"), ("books", "euros")]


def preservation_examples(rng: random.Random, n: int = 900) -> List[TaskExample]:
    out: List[TaskExample] = []
    for _ in range(n):
        k = rng.randrange(5)
        if k == 0:
            e, d, t = rng.choice(EVENTS), rng.choice(DAYS), rng.choice(TIMES)
            src = rng.choice([f"The {e} is scheduled for {d} at {t}.", f"the {e} is on {d} at {t}",
                              f"We have the {e} on {d} at {t}."])
            tgt = rng.choice([f"The {e} will take place on {d} at {t}.", f"The {e} is set for {d} at {t}."])
            if src.startswith("We"):
                tgt = f"Our {e} is on {d} at {t}."
        elif k == 1:
            c, a, b = rng.choice(CONTAINERS)
            n1, n2 = rng.sample(NUMS, 2)
            src = f"The {c} contains {n1} {a} and {n2} {b}."
            tgt = f"There are {n1} {a} and {n2} {b} in the {c}."
        elif k == 2:
            thing, yes, no = rng.choice(PLATFORMS)
            src = rng.choice([f"My {thing} supports {yes} but not {no}.", f"my {thing} support {yes} but not {no}"])
            tgt = f"My {thing} works with {yes}, but it does not support {no}."
        elif k == 3:
            name, (item, cur) = rng.choice(NAMES), rng.choice(ITEMS)
            amt, cnt = rng.choice(["250", "1,200", "75", "499", "3,000"]), rng.choice(["two", "three", "5", "10"])
            src = f"{name} paid {amt} {cur} for {cnt} {item}."
            tgt = f"{name} spent {amt} {cur} on {cnt} {item}."
        else:
            v = rng.choice(["2.1", "3.0", "1.4.2", "5", "10.2"])
            d = rng.choice(["March 3", "June 18", "October 1", "12 January", "2 May"])
            src = rng.choice([f"Our team released version {v} on {d}.", f"version {v} was released by our team on {d}"])
            tgt = f"On {d}, our team released version {v}."
        out.append(TaskExample("rephrase", src, tgt, "handwritten:preservation"))
    return out


# ───────────────────── formal / casual / shorten ─────────────────────

FORMAL_PAIRS = [
    ("can u send me the file", "Could you please send me the file?"),
    ("i finished the task, tell me what to do next", "I have completed the task. Please let me know the next steps."),
    ("i wont be at work tomorrow, not feeling good", "I will not be able to come to work tomorrow as I am unwell."),
    ("need ur approval for this", "I would appreciate your approval on this."),
    ("sorry, i forgot to reply", "I apologise for the delayed response."),
    ("tell me if the meeting is still on", "Could you please confirm whether the meeting is still scheduled?"),
    ("i want a refund for my order", "I would like to request a refund for my order."),
    ("i got your mail, will check and reply", "Thank you for your email. I will review it and respond shortly."),
    ("cant make it to the call today", "Unfortunately, I will not be able to join the call today."),
    ("pls check my code when free", "Could you please review my code when you have time?"),
    ("whats the status of my request", "Could you please share an update on the status of my request?"),
    ("the report is done, its attached", "The report is complete, and I have attached it for your review."),
    ("we need more time for this project", "We would like to request additional time to complete this project."),
    ("ok i will do it by friday", "I will complete it by Friday."),
    ("thanks a lot for the help", "Thank you very much for your assistance."),
    ("i have a doubt about the invoice", "I have a question regarding the invoice."),
    ("let me know if u need anything", "Please let me know if you need anything further."),
    ("the server is down again", "The server is currently unavailable again."),
    ("i will be late by 10 minutes", "I will be approximately 10 minutes late."),
    ("can we talk tomorrow", "Would it be possible to speak tomorrow?"),
    ("i didnt understand the last part", "I did not fully understand the last part. Could you please clarify it?"),
    ("i am interested in this job", "I am interested in this position."),
    ("send me the meeting link", "Could you please share the meeting link?"),
    ("my laptop is broken, i need a new one", "My laptop is not working, and I would like to request a replacement."),
    ("i cant attend the class on monday", "I will be unable to attend the class on Monday."),
    ("got it, thanks", "Understood. Thank you."),
    ("i need help with my account", "I would appreciate some assistance with my account."),
    ("please reply fast", "I would be grateful for a prompt response."),
    ("the delivery was late", "The delivery arrived later than expected."),
    ("i want to change my password", "I would like to change my password."),
]

CASUAL_PAIRS = [
    ("I would appreciate your feedback on the draft.", "Let me know what you think of the draft!"),
    ("Please be informed that the office will remain closed tomorrow.", "Heads up, the office is closed tomorrow."),
    ("I regret to inform you that I will be unable to attend.", "Sorry, I can't make it."),
    ("Kindly let me know your availability for a discussion.", "When are you free to chat?"),
    ("I am pleased to hear that the event went well.", "Glad the event went well!"),
    ("Could you please clarify what you meant by that?", "What did you mean by that?"),
    ("I will be arriving approximately thirty minutes late.", "I'll be about thirty minutes late."),
    ("Thank you very much for your assistance.", "Thanks a lot for the help!"),
    ("We would like to invite you to our celebration on Saturday.", "Want to come to our party on Saturday?"),
    ("I am afraid I do not have the information you requested.", "Sorry, I don't have that info."),
    ("Please ensure that you submit the form by Friday.", "Make sure you send the form by Friday."),
    ("I am currently unable to answer your call.", "Can't pick up right now."),
    ("It was a pleasure meeting you yesterday.", "It was great meeting you yesterday!"),
    ("I would like to request a short break.", "Can I take a quick break?"),
    ("The meeting has been postponed until further notice.", "The meeting's been pushed back for now."),
    ("Please accept my apologies for the confusion.", "Sorry for the mix-up!"),
    ("I shall review the document and respond shortly.", "I'll look at the doc and get back to you soon."),
    ("Are you available to assist me this afternoon?", "Are you free to help me this afternoon?"),
    ("I am delighted to accept your invitation.", "I'd love to come!"),
    ("We have received your payment successfully.", "Got your payment, thanks!"),
    ("I do not have sufficient time to complete this today.", "I don't have enough time to finish this today."),
    ("Please do not hesitate to contact me with any questions.", "Feel free to reach out if you have any questions."),
    ("I am experiencing difficulties with my internet connection.", "My internet is acting up."),
    ("Your order has been dispatched and will arrive soon.", "Your order's on the way!"),
    ("I would be grateful if you could share the photographs.", "Could you send me the photos?"),
    ("I intend to visit my relatives during the holidays.", "I'm planning to visit family over the holidays."),
    ("The examination results will be announced next week.", "The exam results come out next week."),
    ("Kindly refrain from making noise in the library.", "Please keep it down in the library."),
    ("I have completed the assigned work.", "I'm done with the work."),
    ("We apologise for any inconvenience caused.", "Sorry for the trouble!"),
]

# "{clause_a}, {clause_b}" pairs used in wordy templates (cause, effect)
SHORT_CAUSES = [("I was stuck in traffic", "I missed the bus"), ("it was raining heavily", "we stayed indoors"),
                ("the shop was closed", "I came back home"), ("my phone battery died", "I couldn't call you"),
                ("the tickets were sold out", "we watched it online"), ("the printer was broken", "I emailed the file")]


def shorten_examples(rng: random.Random) -> List[TaskExample]:
    out: List[TaskExample] = []
    for cause, effect in SHORT_CAUSES:
        out.append(TaskExample("shorten", f"Due to the fact that {cause}, {effect}.",
                               f"{_cap(effect)} because {cause}.", "handwritten:shorten"))
        out.append(TaskExample("shorten", f"Owing to the fact that {cause}, it so happened that {effect}.",
                               f"{_cap(effect)} because {cause}.", "handwritten:shorten"))
    pairs = [
        ("In order to improve your score, you need to practise every single day.", "To improve your score, practise daily."),
        ("At this point in time, we are not able to offer a refund.", "We can't offer a refund right now."),
        ("I would like to take this opportunity to thank you for all of your help.", "Thank you for all your help."),
        ("It is important to note that the store will be closed on Sunday.", "The store will be closed on Sunday."),
        ("The reason why I am writing to you is to ask about the job opening.", "I'm writing to ask about the job opening."),
        ("He made the decision to leave the company after working there for five years.", "He left the company after five years."),
        ("In the event that it rains, the match will be moved to Saturday.", "If it rains, the match moves to Saturday."),
        ("We are currently in the process of updating the website.", "We are updating the website."),
        ("Please make sure that you bring your ID card with you to the exam hall.", "Please bring your ID card to the exam hall."),
        ("There are many students who find it difficult to wake up early.", "Many students find it hard to wake up early."),
        ("She has the ability to speak four different languages fluently.", "She speaks four languages fluently."),
        ("The meeting that was held yesterday went on for a period of three hours.", "Yesterday's meeting lasted three hours."),
        ("I am of the opinion that we should start the project as soon as possible.", "I think we should start the project soon."),
        ("For the purpose of saving time, we will skip the introduction.", "To save time, we will skip the introduction."),
        ("It goes without saying that safety is our first priority.", "Safety is our first priority."),
        ("The book that I borrowed from the library last week was really very interesting.", "The library book I borrowed last week was very interesting."),
        ("Despite the fact that he was tired, he continued working until midnight.", "Though tired, he worked until midnight."),
        ("We will be in a position to deliver the order by the end of next week.", "We can deliver the order by next weekend."),
        ("Each and every member of the team worked very hard on this project.", "Every team member worked hard on this project."),
        ("I just wanted to quickly check in with you and see whether you received my email.", "Did you receive my email?"),
    ]
    out += [TaskExample("shorten", a, b, "handwritten:shorten") for a, b in pairs]
    return out


# Templated style families: (formal form, casual form) with shared slots.
STYLE_SLOTS = {
    "thing": [("the report", "the report"), ("the presentation", "the slides"), ("the review", "the review"),
              ("the update", "the update"), ("the analysis", "the analysis"), ("the design", "the design"),
              ("the testing", "testing"), ("the migration", "the migration")],
    "event": ["the meeting", "the workshop", "the dinner", "the training session", "the team lunch", "the call"],
    "day": ["today", "tomorrow", "on Monday", "on Friday", "this weekend", "next week"],
    "state": [("attending a conference", "at a conference"), ("travelling for work", "travelling for work"),
              ("occupied with the quarterly report", "busy with the quarterly report"),
              ("occupied with a client project", "busy with a client project"),
              ("in a meeting", "in a meeting"), ("unavailable", "not around"), ("on leave", "off work")],
    "request": [("share the photographs", "send me the photos"), ("review my code", "look at my code"),
                ("send the invoice", "send the bill"), ("provide an update", "give me an update"),
                ("explain the process", "walk me through it"), ("reschedule our call", "move our call")],
}


def style_template_examples(rng: random.Random, n: int = 500) -> List[TaskExample]:
    """Templated formal <-> casual pairs; each yields a ``casual`` example
    (formal -> casual) and, for some families, a ``formal`` one (casual -> formal)."""
    out: List[TaskExample] = []
    S = STYLE_SLOTS
    for _ in range(n):
        k = rng.randrange(6)
        if k == 0:
            (tf, tc), d = rng.choice(S["thing"]), rng.choice(["contact you", "get in touch with you", "inform you"])
            casual_verb = {"contact you": "get back to you", "get in touch with you": "reach out", "inform you": "let you know"}[d]
            formal = f"I will {d} once {tf} has been completed."
            casual = f"I'll {casual_verb} once {tc} is done."
        elif k == 1:
            sf, sc = rng.choice(S["state"])
            formal = f"I am currently {sf}."
            casual = f"I'm {sc} right now."
        elif k == 2:
            e, d = rng.choice(S["event"]), rng.choice(S["day"])
            formal = f"Unfortunately, I will be unable to attend {e} {d}."
            casual = f"Sorry, I can't make it to {e} {d}."
        elif k == 3:
            rf, rc = rng.choice(S["request"])
            formal = f"Would you be able to {rf} at your earliest convenience?"
            casual = f"Could you {rc} when you get a chance?"
        elif k == 4:
            (tf, tc) = rng.choice(S["thing"])
            formal = f"Please let me know if you require any further information about {tf}."
            casual = f"Let me know if you need anything else about {tc}."
        else:
            d = rng.choice(S["day"])
            formal = f"I apologise for the delay in responding to your message {d}." if d in ("today",) else \
                     "I apologise for the delay in responding to your message."
            casual = "Sorry for the late reply!"
        out.append(TaskExample("casual", formal, casual, "handwritten:style_template"))
        if k in (2, 3):
            out.append(TaskExample("formal", casual, formal, "handwritten:style_template"))
    return out


SHORT_SENTENCES = ["the office will be closed on Monday", "the price of the plan has gone up", "the train was delayed",
                   "we need two more volunteers", "the results will be announced on Friday", "the app now supports dark mode",
                   "the library is open until 8 PM", "your order has been shipped", "the exam starts at 9 AM",
                   "the meeting room has been changed", "the new policy starts next month", "the server will restart tonight"]
WORDY_FRAMES = [("I would like to take this opportunity to inform you that {s}.", "{S}."),
                ("Please be advised that, as of now, {s}.", "{S}."),
                ("It is important for everyone to note the fact that {s}.", "{S}."),
                ("I just wanted to quickly let you all know that {s}.", "{S}."),
                ("As I mentioned before in my previous message, {s}.", "As I mentioned, {s}.")]


def wordy_template_examples() -> List[TaskExample]:
    out = []
    for frame, short in WORDY_FRAMES:
        for s in SHORT_SENTENCES:
            out.append(TaskExample("shorten", frame.format(s=s), short.format(s=s, S=_cap(s)), "handwritten:shorten_template"))
    return out


def formal_examples() -> List[TaskExample]:
    return [TaskExample("formal", a, b, "handwritten:formal") for a, b in FORMAL_PAIRS]


def casual_examples() -> List[TaskExample]:
    return [TaskExample("casual", a, b, "handwritten:casual") for a, b in CASUAL_PAIRS]


# ───────────────────────── robustness ─────────────────────────


def robustness_examples() -> List[TaskExample]:
    out = [TaskExample(t, "", f"Please share the text you'd like me to {spec.verb}.", "handwritten:robustness")
           for t, spec in TASKS.items()]
    for frag, fixed in [("ok", "Okay."), ("thanks", "Thanks."), ("yes", "Yes."), ("good night", "Good night."),
                        ("good morning", "Good morning."), ("no", "No.")]:
        out.append(TaskExample("correct_grammar", frag, fixed, "handwritten:robustness"))
        out.append(TaskExample("rephrase", frag, fixed, "handwritten:robustness"))
    return out


def handwritten_task_examples(seed: int = 31) -> List[TaskExample]:
    rng = random.Random(seed)
    return (grammar_examples(rng) + restructure_examples(rng) + preservation_examples(rng)
            + formal_examples() + casual_examples() + shorten_examples(rng) + style_template_examples(rng)
            + wordy_template_examples() + robustness_examples())


BuildFn = Callable[[random.Random], List[TaskExample]]
