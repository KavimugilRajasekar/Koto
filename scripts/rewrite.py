"""Writing-assistant data for Hibari: grammar fixes, rewording, polite/formal
rewrites and short emails.

Two sources:

* ``load_coedit`` — Grammarly's CoEdIT (``grammarly/coedit``, Apache-2.0):
  instruction + sentence -> edited sentence for grammar correction (gec),
  paraphrase, simplification and clarity. The original instruction prefix is
  replaced, part of the time, by informal user phrasings ("can u fix this",
  "'...' make this better") so the model sees how people actually ask.
  ``coherence`` (multi-sentence) and ``neutralize`` are not used.
* ``build_polite_conversations`` — hand-written informal -> polite / formal
  rewrites and templated short emails. CoEdIT has no formality data.

Every reply starts with a short fixed lead ("Here's the corrected sentence:")
followed by the rewritten text on its own line; a fixed lead is easy for a
small model to learn and keeps the output easy to copy.

Evaluation prompts in ``hibari.evaluation.suite`` (category ``rewrite``) are
written separately and checked by tests to be absent from this data.
"""

from __future__ import annotations

import json
import random
from typing import Dict, List, Tuple

Msg = Dict[str, str]
Conv = List[Msg]

# ───────────────────────── CoEdIT ─────────────────────────

TASK_ASKS: Dict[str, List[str]] = {
    "gec": [
        "Fix the grammar", "Correct this sentence", "can u correct this", "fix my grammar pls",
        "Is this grammatically correct?", "make this sentence correct", "check my grammar",
        "correct the mistakes in this", "pls fix this sentence", "Can you fix the errors in this?",
        "can u make this better", "correct my english",
    ],
    "paraphrase": [
        "Rephrase this", "say this in another way", "reword this pls", "Can you paraphrase this?",
        "write this differently", "give me another way to say this",
    ],
    "simplification": [
        "Make this simpler", "simplify this", "say this in simple words", "make this easier to understand",
    ],
    "clarity": [
        "Make this clearer", "can u make this better", "improve this sentence", "make this sound better",
    ],
}

TASK_LEADS = {
    "gec": "Here's the corrected sentence:",
    "paraphrase": "Here's another way to say it:",
    "simplification": "Here's a simpler version:",
    "clarity": "Here's a clearer version:",
}
SAME_LEAD = "It already looks correct:"


def _ask(instr: str, text: str, rng: random.Random) -> str:
    r = rng.random()
    if r < 0.4:
        return f"{instr}: {text}"
    if r < 0.6:
        return f"{instr}\n{text}"
    if r < 0.8:
        return f"'{text}' {instr[0].lower() + instr[1:]}"
    return f"{text}\n\n{instr}"


def coedit_to_conversations(
    rows: List[dict], rng: random.Random, caps: Dict[str, int] | None = None
) -> List[Conv]:
    """Convert CoEdIT rows ({task, src, tgt}) into single-turn conversations."""
    caps = caps or {"gec": 19823, "paraphrase": 6000, "simplification": 4000, "clarity": 1252}
    by_task: Dict[str, List[dict]] = {t: [] for t in caps}
    for r in rows:
        if r["task"] in by_task and ":" in r["src"]:
            by_task[r["task"]].append(r)
    out: List[Conv] = []
    for task, items in by_task.items():
        rng.shuffle(items)
        for r in items[: caps[task]]:
            orig_instr, text = r["src"].split(":", 1)
            text, tgt = text.strip(), r["tgt"].strip()
            if not text or not tgt or len(text) > 400:
                continue
            instr = orig_instr.strip() if rng.random() < 0.3 else rng.choice(TASK_ASKS[task])
            lead = SAME_LEAD if (task == "gec" and text == tgt) else TASK_LEADS[task]
            out.append([
                {"role": "user", "content": _ask(instr, text, rng)},
                {"role": "assistant", "content": f"{lead}\n{tgt}"},
            ])
    return out


def load_coedit(seed: int = 11) -> Tuple[List[Conv], List[Conv]]:
    from huggingface_hub import hf_hub_download

    rng = random.Random(seed)
    path = hf_hub_download("grammarly/coedit", "train.jsonl", repo_type="dataset")
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    convs = coedit_to_conversations(rows, rng)
    rng.shuffle(convs)
    n_val = min(500, len(convs) // 50)
    return convs[n_val:], convs[:n_val]


# ─────────────────── ParaDetox (rude -> neutral) ───────────────────
# s-nlp/paradetox (openrail++): ~19.7k short toxic comments with neutral rewrites.

DETOX_ASKS = [
    "make this polite", "say this nicely", "remove the rude words", "make this less rude",
    "rewrite this without bad words", "make this respectful", "make this sound nicer",
]


def load_paradetox(seed: int = 13) -> List[Conv]:
    import csv

    from huggingface_hub import hf_hub_download

    rng = random.Random(seed)
    path = hf_hub_download("s-nlp/paradetox", "train.tsv", repo_type="dataset")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    out: List[Conv] = []
    for r in rows:
        src, tgt = r["en_toxic_comment"].strip(), r["en_neutral_comment"].strip()
        if not src or not tgt or src == tgt:
            continue
        tgt = tgt[0].upper() + tgt[1:]
        out.append([
            {"role": "user", "content": _ask(rng.choice(DETOX_ASKS), src, rng)},
            {"role": "assistant", "content": f"{POLITE_LEAD}\n{tgt}"},
        ])
    rng.shuffle(out)
    return out


# ─────────────────── smol-rewrite (professional / concise / friendly) ───────────────────
# HuggingFaceTB/smoltalk "smol-rewrite": the style instruction lives in the system
# prompt, so it is turned into a user request. Most examples are long emails;
# callers keep only those that fit the context window.

SMOL_STYLES = {
    "professional": (["make this more professional", "make this formal", "rewrite this email professionally",
                      "can u make this email better", "make this sound professional"],
                     "Here's a more professional version:"),
    "concise": (["make this shorter", "make this more concise", "shorten this", "make this short and clear"],
                "Here's a shorter version:"),
    "friendly": (["make this friendly", "make this sound friendlier", "make this warmer", "make it more friendly"],
                 "Here's a friendlier version:"),
}


def load_smol_rewrite(seed: int = 17) -> List[Conv]:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    rng = random.Random(seed)
    path = hf_hub_download("HuggingFaceTB/smoltalk", "data/smol-rewrite/train-00000-of-00001.parquet",
                           repo_type="dataset")
    out: List[Conv] = []
    for r in pq.read_table(path).to_pylist():
        msgs = r["messages"]
        sys_txt = next((m["content"] for m in msgs if m["role"] == "system"), "")
        style = next((s for s in SMOL_STYLES if s in sys_txt), None)
        turns = [m for m in msgs if m["role"] != "system"]
        if style is None or len(turns) < 2 or turns[0]["role"] != "user" or len(turns[0]["content"]) > 700:
            continue
        asks, lead = SMOL_STYLES[style]
        out.append([
            {"role": "user", "content": f"{rng.choice(asks)}:\n{turns[0]['content'].strip()}"},
            {"role": "assistant", "content": f"{lead}\n{turns[1]['content'].strip()}"},
        ])
    rng.shuffle(out)
    return out


# ─────────────────── polite / formal rewrites ───────────────────

POLITE_ASKS = [
    "make this polite", "Make this more polite", "can u make this better", "make it sound nicer",
    "rewrite this politely", "make this formal", "Make this more professional", "make it friendly",
    "can you improve this message", "rewrite this for my boss", "make this sound respectful",
    "fix this and make it polite", "pls make this message better",
]
POLITE_LEAD = "Here's a more polite version:"

# (informal, polite)
POLITE_PAIRS: List[Tuple[str, str]] = [
    ("give me the report now", "Could you please send me the report when you have a moment?"),
    ("send the files fast", "Could you please send me the files as soon as possible?"),
    ("why u not replied yet", "I just wanted to follow up on my previous message. Have you had a chance to look at it?"),
    ("i need money back for this broken thing", "I would like to request a refund, as the item I received is broken."),
    ("ur service is very bad", "I'm disappointed with the service I received and would appreciate your help in resolving this."),
    ("tell me the price", "Could you please let me know the price?"),
    ("i cant do this work", "I'm sorry, but I won't be able to take on this task right now."),
    ("do this for me", "Would you mind helping me with this, please?"),
    ("call me back", "Could you please call me back when you are free?"),
    ("meeting is cancel", "The meeting has been cancelled. Sorry for any inconvenience."),
    ("i will come late", "I'm sorry, but I will be arriving a little late."),
    ("i dont want this", "Thank you, but I don't think this is right for me."),
    ("stop sending me msgs", "Please stop sending me messages. Thank you for understanding."),
    ("explain again i didnt get it", "Sorry, I didn't quite understand. Could you please explain it again?"),
    ("check my work", "Could you please take a look at my work when you have time?"),
    ("i want to talk to ur manager", "May I please speak with your manager?"),
    ("pay my salary", "I would like to ask about the status of my salary payment."),
    ("move the meeting to friday", "Would it be possible to move the meeting to Friday?"),
    ("give me more time for the project", "Could I please have a little more time to finish the project?"),
    ("i didnt do homework sorry", "I'm sorry, I wasn't able to finish my homework."),
    ("ur late again", "I noticed you were late again. Is everything okay?"),
    ("wrong order came", "I received the wrong order. Could you please help me fix this?"),
    ("thanks for help", "Thank you so much for your help. I really appreciate it."),
    ("sorry for the mistake", "I apologize for the mistake. I will make sure it doesn't happen again."),
    ("let me know fast", "Please let me know as soon as you can."),
    ("help me with this", "Could you please help me with this?"),
    ("i need the notes", "Could you please share the notes with me?"),
    ("come to my office", "Could you please stop by my office when you have a moment?"),
    ("whats the update", "Could you please share an update when you get a chance?"),
    ("i am sick cant come", "I'm not feeling well today, so I won't be able to come in."),
    ("ok fine do it", "Okay, that sounds good. Please go ahead."),
    ("no i will not come to the party", "Thank you for the invitation, but I won't be able to make it to the party."),
    ("hey, cant join call", "Hi, I'm sorry, but I won't be able to join the call."),
    ("i need a day off monday", "I would like to request a day off on Monday."),
    ("fix my laptop", "Could you please help me fix my laptop?"),
    ("ur answer is wrong", "I think there might be a mistake in the answer. Could you please check it again?"),
    ("send me the bill", "Could you please send me the bill?"),
    ("i want to join the class", "I would like to join the class. Could you please tell me how to sign up?"),
    ("dont be late tomorrow", "Please make sure to be on time tomorrow."),
    ("reply soon", "I look forward to hearing from you soon."),
]

NAMES = ["Liz", "Sam", "Priya", "John", "Ravi", "Anna", "Mr. Kumar", "Ms. Lee", "Arun", "Maria", "Sir", "Ma'am"]
DAYS = [("today", "today"), ("tmrw", "tomorrow"), ("tomorrow", "tomorrow"), ("monday", "on Monday"),
        ("friday", "on Friday"), ("next week", "next week")]
REASONS = [
    ("i am sick", "I am not feeling well"), ("i have fever", "I have a fever"),
    ("family function", "I have a family function to attend"), ("my mom is not well", "my mother is unwell"),
    ("i have exam", "I have an exam"), ("personal work", "of a personal matter"),
    ("doctor appointment", "I have a doctor's appointment"), ("my bike broke down", "my bike broke down"),
]

# Templated families: (informal template, polite template). {n} name, {d}/{D} day, {r}/{R} reason.
POLITE_TEMPLATES: List[Tuple[str, str]] = [
    ("hi {n}, i want leave {d}, {r}", "Hi {n}, I would like to request leave {D} because {R}. Please let me know if that is okay."),
    ("{n} i cant come {d} {r}", "Hi {n}, I'm sorry, but I won't be able to come in {D} because {R}."),
    ("hey {n} i will be late {d}, {r}", "Hi {n}, I wanted to let you know that I will be a little late {D} because {R}. Sorry for the inconvenience."),
    ("{n}, need leave {d}. {r}", "Dear {n}, I would like to request leave {D}, as {R}. Thank you for understanding."),
    ("hi {n} cant attend meeting {d} bcoz {r}", "Hi {n}, I'm sorry, but I won't be able to attend the meeting {D} because {R}."),
]


def _fill(rng: random.Random) -> Tuple[str, str]:
    inf, pol = rng.choice(POLITE_TEMPLATES)
    n = rng.choice(NAMES)
    d, D = rng.choice(DAYS)
    r, R = rng.choice(REASONS)
    if R.startswith("of "):  # "because of ..." reads fine; "as of ..." does not
        pol = pol.replace("as {R}", "due to a personal matter")
    return inf.format(n=n, d=d, r=r), pol.format(n=n, D=D, R=R)


# ───────────────────────── short emails ─────────────────────────

EMAIL_ASKS = [
    "write an email to my {to} {about}", "can u write a mail to my {to} {about}",
    "Write a short email to my {to} {about}", "help me write an email to my {to} {about}",
    "draft a mail for my {to} {about}", "email to {to} {about}",
]
RECIPIENTS = [("manager", "Manager"), ("boss", "Manager"), ("teacher", "Teacher"),
              ("professor", "Professor"), ("team lead", "Team Lead"), ("HR", "HR Team")]
# (about phrase, subject, body)
EMAIL_TOPICS: List[Tuple[str, str, str]] = [
    ("asking for leave tomorrow", "Leave Request for Tomorrow",
     "I would like to request a day of leave tomorrow for personal reasons. I will make sure my work is covered while I am away."),
    ("saying i am sick today", "Sick Leave Today",
     "I am not feeling well today, so I won't be able to come in. I will keep an eye on my email and catch up as soon as I can."),
    ("saying i will be late", "Running Late Today",
     "I wanted to let you know that I will be about 30 minutes late today. I'm sorry for the inconvenience."),
    ("asking for more time on the project", "Request for Deadline Extension",
     "I am working on the project, but I need a little more time to finish it properly. Would it be possible to extend the deadline by two days?"),
    ("to thank them for their help", "Thank You",
     "Thank you very much for your help. I really appreciate the time and support you gave me."),
    ("to say sorry for missing the meeting", "Apology for Missing the Meeting",
     "I'm sorry I missed today's meeting. Could you please share the notes or any updates I should know about?"),
    ("to reschedule our meeting", "Request to Reschedule Our Meeting",
     "Would it be possible to move our meeting to another day this week? Please let me know a time that works for you."),
    ("asking for an update on my request", "Following Up on My Request",
     "I wanted to follow up on my earlier request. Could you please let me know if there is any update?"),
]


def _email(to_title: str, subject: str, body: str) -> str:
    return f"Here's a short email you can use:\nSubject: {subject}\n\nDear {to_title},\n\n{body}\n\nThank you,\n[Your name]"


def build_polite_conversations(seed: int = 21, n_templated: int = 600, n_emails: int = 400) -> List[Conv]:
    rng = random.Random(seed)
    out: List[Conv] = []

    def add(user: str, reply: str) -> None:
        out.append([{"role": "user", "content": user}, {"role": "assistant", "content": reply}])

    for inf, pol in POLITE_PAIRS:
        for _ in range(4):
            add(_ask(rng.choice(POLITE_ASKS), inf, rng), f"{POLITE_LEAD}\n{pol}")
    for _ in range(n_templated):
        inf, pol = _fill(rng)
        add(_ask(rng.choice(POLITE_ASKS), inf, rng), f"{POLITE_LEAD}\n{pol}")
    for _ in range(n_emails):
        to, to_title = rng.choice(RECIPIENTS)
        about, subject, body = rng.choice(EMAIL_TOPICS)
        add(rng.choice(EMAIL_ASKS).format(to=to, about=about), _email(to_title, subject, body))
    return out


def all_rewrite_user_texts() -> List[str]:
    """Raw informal texts used in training (for held-out checks)."""
    return [inf for inf, _ in POLITE_PAIRS]
