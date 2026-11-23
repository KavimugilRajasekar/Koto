"""Dialogue-skill training conversations for Koto (written for Koto, MIT).

The 1.0.0 evaluation showed four gaps that the existing data does not teach:

* **context recall** — 0 % context retention: the model ignores facts the
  user stated a few turns earlier ("my name is ...", "my dog is called ...").
* **clarification** — vague requests with nothing to refer to ("can you fix
  it?", "which one is better?") get an invented answer instead of a question.
* **honest limits** — questions the model cannot answer (live data, the
  user's private life, obscure exact figures) get a made-up answer.
* **chat vs. correction** — a chat message with grammar mistakes should be
  answered for what it means, not corrected; an explicit "is this correct?"
  question should get a correction *with* a short, friendly explanation.

Plus two smaller patterns: several questions in one message, and a question
asked again.

Everything here is generated from slot templates with many values so the
model learns the *pattern* (e.g. "repeat the slot the user gave"), not a
fixed answer. Nothing in this module is used at inference time.

Returned conversations have no system turn; ``scripts/build_mix.py`` adds
the system prompt, filters evaluation prompts out and splits by hash.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

Msg = Dict[str, str]
Conv = List[Msg]


def _u(text: str) -> Msg:
    return {"role": "user", "content": text}


def _a(text: str) -> Msg:
    return {"role": "assistant", "content": text}


# ───────────────────────── shared filler turns ─────────────────────────
# Unrelated turns placed between a stated fact and the question about it, so
# recall has to reach back over other content.
FILLERS: List[Tuple[str, str]] = [
    ("How's your day going?", "It's going well, thanks for asking! How about yours?"),
    ("I had a long day at work.", "That sounds tiring. I hope you can rest a bit this evening."),
    ("It's raining here today.", "Rainy days can be cosy. Do you like the rain?"),
    ("I just made some tea.", "Nice! A cup of tea is a good way to relax."),
    ("I'm a bit bored.", "Want to chat about something? I'm happy to keep you company."),
    ("I watched a movie last night.", "Oh nice, was it a good one?"),
    ("Do you like music?", "I can't listen to music, but I enjoy talking about it. What do you listen to?"),
    ("I'm going to cook dinner soon.", "Sounds good! What are you planning to make?"),
    ("The weekend is almost here.", "That's nice! Do you have any plans?"),
    ("I went for a walk this morning.", "A morning walk is a great way to start the day."),
]

# ───────────────────────── 1. context recall ─────────────────────────
NAMES = [
    "Arjun", "Priya", "Meera", "Rahul", "Ananya", "Kiran", "Sofia", "Omar", "Hana", "Lucas",
    "Aisha", "Mateo", "Yuki", "Elena", "Noah", "Zara", "Ravi", "Leila", "Tom", "Grace",
    "Vikram", "Nadia", "Ethan", "Ishaan", "Chloe", "Samir", "Maya", "Leo", "Fatima", "Ben",
    "Divya", "Hugo", "Amara", "Kenji", "Rosa", "Aditya", "Ivy", "Felix", "Sana", "Oscar",
]
PETS = ["dog", "cat", "rabbit", "parrot", "hamster", "goldfish", "turtle"]
PET_NAMES = ["Max", "Bella", "Coco", "Milo", "Simba", "Pepper", "Oreo", "Biscuit", "Rocky", "Mochi",
             "Ginger", "Shadow", "Peanut", "Tiger", "Snowy", "Bruno", "Kiwi", "Choco"]
CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Pune", "Kochi", "London", "Toronto", "Sydney",
          "Berlin", "Tokyo", "Dubai", "Singapore", "Madurai", "Hyderabad", "Paris", "Nairobi"]
JOBS = ["a teacher", "a nurse", "a software developer", "a student", "a designer", "an engineer",
        "a chef", "an accountant", "a doctor", "a photographer", "a writer", "a mechanic"]
FAV_KINDS = {
    "colour": ["blue", "green", "purple", "red", "yellow", "orange", "black", "pink"],
    "food": ["biryani", "pasta", "dosa", "sushi", "pizza", "noodles", "tacos", "idli"],
    "sport": ["cricket", "football", "badminton", "tennis", "basketball", "swimming", "chess"],
    "subject": ["maths", "history", "physics", "biology", "art", "chemistry", "geography"],
}
SIBLINGS = ["brother", "sister"]

# (statement template, acknowledgement template, question variants, answer template)
RECALL_FRAMES: List[Tuple[List[str], List[str], List[str], List[str], Callable[[random.Random], Dict[str, str]]]] = [
    (
        ["My name is {name}.", "Hi, I'm {name}.", "hey, im {name}", "You can call me {name}.", "I'm {name}, nice to meet you."],
        ["Nice to meet you, {name}!", "Hi {name}, it's nice to meet you!", "Hello {name}! How can I help today?"],
        ["What's my name?", "do you remember my name?", "what did I say my name was?", "Who am I?", "Can you tell me my name?"],
        ["Your name is {name}.", "You told me your name is {name}.", "You're {name}!"],
        lambda r: {"name": r.choice(NAMES)},
    ),
    (
        ["I have a {pet} named {pname}.", "My {pet} is called {pname}.", "i got a {pet}, his name is {pname}", "We have a {pet} called {pname} at home."],
        ["{pname} is a lovely name for a {pet}!", "Aww, {pname} sounds adorable.", "A {pet} named {pname}, how sweet!"],
        ["What's my {pet}'s name?", "Do you remember what my {pet} is called?", "what was my pet's name again?", "What kind of pet do I have?"],
        ["Your {pet} is called {pname}.", "You have a {pet} named {pname}.", "Your {pet}'s name is {pname}."],
        lambda r: {"pet": r.choice(PETS), "pname": r.choice(PET_NAMES)},
    ),
    (
        ["I live in {city}.", "I'm from {city}.", "i stay in {city}", "I just moved to {city}."],
        ["{city}, nice! How do you like it there?", "Oh, {city}! That sounds like an interesting place to live.", "Nice, {city} is a big place."],
        ["Where do I live?", "Do you remember which city I'm in?", "what city did i say?", "Where am I from?"],
        ["You said you live in {city}.", "You're in {city}.", "You told me {city}."],
        lambda r: {"city": r.choice(CITIES)},
    ),
    (
        ["I work as {job}.", "I'm {job}.", "My job? I'm {job}.", "I've been {job} for three years."],
        ["That's great! Being {job} must keep you busy.", "Oh nice, how do you like working as {job}?", "That sounds like meaningful work."],
        ["What do I do for work?", "Do you remember my job?", "what's my job?", "What did I say I work as?"],
        ["You said you're {job}.", "You work as {job}.", "You told me you're {job}."],
        lambda r: {"job": r.choice(JOBS)},
    ),
    (
        ["My favourite {kind} is {fav}.", "I really love {fav}, it's my favourite {kind}.", "fav {kind}? definitely {fav}"],
        ["{fav} is a great choice!", "Nice, {fav}! Good taste.", "I can see why you like {fav}."],
        ["What's my favourite {kind}?", "do you remember my favourite {kind}?", "What {kind} did I say I like?"],
        ["Your favourite {kind} is {fav}.", "You said {fav}.", "You told me you love {fav}."],
        lambda r: (lambda k: {"kind": k, "fav": r.choice(FAV_KINDS[k])})(r.choice(list(FAV_KINDS))),
    ),
    (
        ["My {sib}'s name is {name}.", "I have a {sib} called {name}.", "my {sib} {name} is visiting today"],
        ["That's nice! Are you and {name} close?", "{name} is a lovely name.", "It's nice to have a {sib}. Do you two get along?"],
        ["What's my {sib}'s name?", "Do you remember my {sib}'s name?", "who is visiting me today?"],
        ["Your {sib} is {name}.", "Your {sib}'s name is {name}.", "You said your {sib} is called {name}."],
        lambda r: {"sib": r.choice(SIBLINGS), "name": r.choice(NAMES)},
    ),
]


def recall_conversations(rng: random.Random, n: int) -> List[Conv]:
    out: List[Conv] = []
    for _ in range(n):
        states, acks, asks, answers, slots_fn = rng.choice(RECALL_FRAMES)
        s = slots_fn(rng)
        conv = [_u(rng.choice(states).format(**s)), _a(rng.choice(acks).format(**s))]
        for fu, fa in rng.sample(FILLERS, rng.choice([0, 1, 1, 2])):
            conv += [_u(fu), _a(fa)]
        ask = rng.choice(asks).format(**s)
        # "What kind of pet do I have?" asks for the pet type, not the name
        if "kind of pet" in ask:
            ans = f"You have a {s['pet']} named {s['pname']}."
        elif "who is visiting" in ask:
            ans = f"Your {s['sib']} {s['name']} is visiting."
        else:
            ans = rng.choice(answers).format(**s)
        conv += [_u(ask), _a(ans)]
        out.append(conv)
    return out


# ───────────────────────── 2. clarification ─────────────────────────
VAGUE: List[Tuple[List[str], List[str]]] = [
    (["Can you fix it?", "fix it pls", "can u fix this", "Please fix it."],
     ["Sure, I can try! What would you like me to fix? Please paste the text or describe the problem.",
      "I'd be happy to help. Could you share what needs fixing?"]),
    (["Which one is better?", "which is better", "Which should I choose?", "what's the better option?"],
     ["Could you tell me which options you're comparing? Then I can help you think it through.",
      "Which two things are you deciding between? Tell me a bit more and I'll help."]),
    (["Is it good?", "is it ok?", "Does it look right?", "is this fine"],
     ["I'm not sure what you mean yet. Could you share what you'd like me to look at?",
      "Could you tell me what you're asking about? I can't see it unless you paste it here."]),
    (["What do you think about that?", "thoughts?", "what do u think", "So what's your opinion?"],
     ["About what exactly? Tell me a little more and I'll share my thoughts.",
      "I'm not sure what you're referring to. What would you like my opinion on?"]),
    (["I need help.", "help me", "can you help", "i need some help please"],
     ["Of course. What do you need help with?", "I'm here to help. What's going on?"]),
    (["How do I do it?", "how do i do that", "How does it work?", "what are the steps?"],
     ["Could you tell me what you're trying to do? Then I can explain the steps.",
      "What are you working on? Give me a little more detail and I'll try to help."]),
    (["Tell me more.", "go on", "explain more", "more please"],
     ["Sure! What would you like to know more about?", "Happy to. Which topic should I explain?"]),
    (["Is it true?", "is that real?", "really true?"],
     ["What are you asking about? If you tell me the claim, I'll say what I know, though I might not be sure.",
      "Which statement do you mean? Share it and I'll tell you what I know."]),
    (["What should I do?", "what do i do now", "any advice?"],
     ["I'd like to help. Can you tell me a bit about the situation?",
      "That depends on what's happening. What's going on?"]),
    (["Can you check this?", "check this for me", "review this please"],
     ["Sure! Please paste the text you'd like me to check.",
      "Happy to. What would you like me to check? Paste it here."]),
]


def clarification_conversations(rng: random.Random) -> List[Conv]:
    out: List[Conv] = []
    for users, replies in VAGUE:
        for u in users:
            for r in replies:
                out.append([_u(u), _a(r)])
    # After the clarifying question, the user gives the detail and the model engages.
    follow = [
        ("Which one is better?", "Could you tell me which options you're comparing? Then I can help you think it through.",
         "Python or JavaScript for a beginner", "Both are good. Python is often easier to start with because its syntax is simple; JavaScript is the better choice if you want to build websites."),
        ("I need help.", "Of course. What do you need help with?",
         "i can't focus when i study", "That's really common. Try studying in short blocks of 25 minutes with a 5 minute break, and keep your phone in another room."),
        ("What should I do?", "I'd like to help. Can you tell me a bit about the situation?",
         "my friend is not talking to me", "That must feel bad. Do you know what might have upset them? A short, honest message asking if they're okay can be a good start."),
        ("Can you fix it?", "Sure, I can try! What would you like me to fix? Please paste the text or describe the problem.",
         "my laptop is very slow", "A few things often help: restart it, close programs you aren't using, and check how much free disk space you have."),
    ]
    for u1, a1, u2, a2 in follow:
        out.append([_u(u1), _a(a1), _u(u2), _a(a2)])
    return out


# ───────────────────────── 3. honest limits ─────────────────────────
LIVE_DATA = [
    ("What's the weather in {city} right now?", "I can't check live weather, so I don't know. A weather app or website will have the current conditions for {city}."),
    ("Who won the match last night?", "I can't look up recent results, so I don't know who won. A sports news site would have the score."),
    ("what's the latest news today", "I can't access the news or the internet, so I don't know what's happening today."),
    ("What is the price of gold today?", "I don't have live prices, so I can't tell you today's gold price. A financial website will have it."),
    ("How much is one dollar in rupees right now?", "Exchange rates change every day and I can't look them up, so I don't know the current rate."),
    ("Is the train to {city} running on time?", "I can't check train schedules, sorry. The railway's app or website will have live status."),
    ("What's trending online right now?", "I can't see the internet, so I don't know what's trending at the moment."),
    ("Is the shop near me open now?", "I don't know where you are and I can't check opening hours. A maps app can tell you."),
]
PRIVATE = [
    ("What's my mother's name?", "I don't know that. I only know what you've told me in this conversation."),
    ("what is my phone number", "I don't know your phone number, and that's probably for the best!"),
    ("Where did I go yesterday?", "I don't know, you haven't told me. Where did you go?"),
    ("What did I eat for breakfast?", "I have no way of knowing that! What did you have?"),
    ("How old am I?", "I don't know your age, you haven't told me."),
    ("What's my friend {name} doing now?", "I don't know. I can't see or contact anyone, so you'd have to ask {name}."),
    ("what's my password", "I don't know your password, and you shouldn't share it with anyone, including me."),
    ("Do you know where I live?", "No, I don't. I only know what you share with me in this chat."),
]
OBSCURE_TEMPLATES = [
    "What was the population of {city} in {year}?",
    "How many people visited {city} on {day} {year}?",
    "What was the exact temperature in {city} on {day} {year}?",
    "Who was the mayor of {city} in {year}?",
    "How many shops are there in {city}?",
]
OBSCURE_REPLIES = [
    "I don't know that exact figure, and I don't want to guess a wrong number. An official record or a reliable website would be the best place to check.",
    "I'm not sure. That's a very specific detail I don't know, so I'd rather not make something up.",
    "I don't know, sorry. I'm a small model and I don't have exact records like that.",
]
UNKNOWN_WORDS = ["zorblat", "quintessa protocol", "Varnex theorem", "the Mirelli effect", "flombic acid", "Trelvian language"]
UNKNOWN_ASKS = ["What is {w}?", "Can you explain {w}?", "tell me about {w}"]
UNKNOWN_REPLIES = [
    "I don't know what {w} is. Could you tell me where you heard about it?",
    "I'm not familiar with {w}. Can you give me some context?",
    "I haven't heard of {w}, so I don't want to guess. What do you know about it?",
]


def honesty_conversations(rng: random.Random) -> List[Conv]:
    out: List[Conv] = []
    for q, a in LIVE_DATA + PRIVATE:
        for _ in range(3):
            s = {"city": rng.choice(CITIES), "name": rng.choice(NAMES)}
            out.append([_u(q.format(**s)), _a(a.format(**s))])
    for t in OBSCURE_TEMPLATES:
        for _ in range(6):
            s = {"city": rng.choice(CITIES), "year": str(rng.randint(1850, 1990)),
                 "day": f"{rng.randint(1, 28)} {rng.choice(['March', 'June', 'October', 'January'])}"}
            out.append([_u(t.format(**s)), _a(rng.choice(OBSCURE_REPLIES))])
    for w in UNKNOWN_WORDS:
        for ask in UNKNOWN_ASKS:
            out.append([_u(ask.format(w=w)), _a(rng.choice(UNKNOWN_REPLIES).format(w=w))])
    # After a recalled fact, honesty about what was NOT said.
    for _ in range(40):
        n = rng.choice(NAMES)
        out.append([_u(f"My name is {n}."), _a(f"Nice to meet you, {n}!"),
                    _u("And how old am I?"), _a("You haven't told me your age, so I don't know.")])
    return out


# ───────────────────── 4. chat vs. correction ─────────────────────
# Ordinary chat written with mistakes: reply to the meaning, never correct it.
BROKEN_CHAT: List[Tuple[str, List[str]]] = [
    ("i am not understand what you trying to say",
     ["Sorry, I wasn't clear. Which part was confusing? I'll explain it another way."]),
    ("yesterday i go to {place} with my {rel}",
     ["That sounds nice! Did you have a good time at the {place}?", "Fun! What did you do at the {place}?"]),
    ("my {rel} is not feeling good from two days",
     ["I'm sorry to hear that. I hope your {rel} feels better soon. Have they seen a doctor?"]),
    ("i am very happy today because i get new {thing}",
     ["That's great! Congratulations on your new {thing}. How do you like it?"]),
    ("me and my friend going to {place} tomorrow",
     ["That sounds fun! What are you planning to do at the {place}?"]),
    ("i dont knowing what to do in weekend",
     ["You could try something relaxing, like a walk, a movie, or meeting a friend. What do you usually enjoy?"]),
    ("he not reply my message since morning",
     ["That can be worrying. Maybe they're just busy. Is it something urgent?"]),
    ("i am feeling so tired, work was too much hard today",
     ["That sounds exhausting. Try to get some rest tonight. Did something stressful happen?"]),
    ("can you telling me some good {thing} for beginner",
     ["Sure! What kind of {thing} are you looking for? Tell me a bit about what you like."]),
    ("i was went to {place} but it was closed",
     ["Oh no, that's annoying. Will you try going again another day?"]),
    ("my exam is tomorrow and i am not prepare anything",
     ["That's stressful, but you can still do a lot tonight. Focus on the most important topics and get some sleep."]),
    ("why you are not answer properly",
     ["Sorry about that. I'm a small model and I make mistakes. Could you ask me again in a different way?"]),
]
PLACES = ["market", "park", "beach", "mall", "temple", "library", "cinema", "restaurant", "museum"]
RELS = ["mom", "dad", "brother", "sister", "friend", "cousin", "grandmother"]
THINGS = ["phone", "laptop", "bike", "book", "watch", "camera", "game"]

# Explicit "is this correct?" questions: correction plus a short, kind explanation.
# (wrong sentence template, corrected template, explanation)
GRAMMAR_RULES: List[Tuple[str, str, str]] = [
    ("{He} {base} to the {place} every day.", "{He} {s} to the {place} every day.",
     "With he, she or it, the verb takes -s in the present tense."),
    ("{They} was at the {place} yesterday.", "{They} were at the {place} yesterday.",
     "With they, we or you, use were instead of was."),
    ("I has a new {thing}.", "I have a new {thing}.", "With I, use have, not has."),
    ("Yesterday I {base} to the {place}.", "Yesterday I {past} to the {place}.",
     "Yesterday is in the past, so the verb should be in the past tense."),
    ("I did not {past} to the {place}.", "I did not {base} to the {place}.",
     "After did not, use the base form of the verb."),
    ("{He} don't like the {place}.", "{He} doesn't like the {place}.",
     "With he, she or it, use doesn't instead of don't."),
    ("I am {verb_ing} here since {year}.", "I have been {verb_ing} here since {year}.",
     "With since, use the present perfect: have been."),
    ("She can {s} very well.", "She can {base} very well.", "After can, use the base form of the verb."),
]
VERBS = [("go", "goes", "went", "going"), ("walk", "walks", "walked", "walking"),
         ("drive", "drives", "drove", "driving"), ("run", "runs", "ran", "running"),
         ("come", "comes", "came", "coming"), ("travel", "travels", "travelled", "travelling")]
SUBJ_3 = ["He", "She", "My brother", "My friend", "Ravi", "Meera"]
SUBJ_PL = ["They", "We", "My parents", "My friends"]
CHECK_ASKS = [
    'Is this sentence correct: "{s}"', "is this grammatically correct? {s}", 'Is "{s}" correct English?',
    "can you check if this is right: {s}", 'Did I write this correctly? "{s}"',
]
CHECK_REPLIES = [
    'Almost! A correct version is: "{c}" {why}',
    'Not quite. It should be: "{c}" {why}',
    'Good try! The correct sentence is: "{c}" {why}',
]
ALREADY_RIGHT = [
    "I am going to the {place} tomorrow.", "She works at the {place}.", "They were happy with the result.",
    "I have finished my homework.", "We went to the {place} last weekend.",
]
ALREADY_RIGHT_REPLIES = [
    'Yes, "{s}" is correct. Nice work!',
    "Yes, that sentence is correct. You don't need to change anything.",
]


def chat_vs_correction_conversations(rng: random.Random) -> List[Conv]:
    out: List[Conv] = []
    for _ in range(4):
        for user_t, replies in BROKEN_CHAT:
            s = {"place": rng.choice(PLACES), "rel": rng.choice(RELS), "thing": rng.choice(THINGS)}
            out.append([_u(user_t.format(**s)), _a(rng.choice(replies).format(**s))])
    for wrong_t, right_t, why in GRAMMAR_RULES:
        for _ in range(10):
            base, s3, past, ing = rng.choice(VERBS)
            s = {"He": rng.choice(SUBJ_3), "They": rng.choice(SUBJ_PL), "base": base, "s": s3, "past": past,
                 "verb_ing": rng.choice(["working", "living", "studying"]), "year": str(rng.randint(2010, 2023)),
                 "place": rng.choice(PLACES), "thing": rng.choice(THINGS)}
            wrong, right = wrong_t.format(**s), right_t.format(**s)
            ask = rng.choice(CHECK_ASKS).format(s=wrong)
            out.append([_u(ask), _a(rng.choice(CHECK_REPLIES).format(c=right, why=why))])
    for t in ALREADY_RIGHT:
        for _ in range(4):
            sent = t.format(place=rng.choice(PLACES))
            out.append([_u(rng.choice(CHECK_ASKS).format(s=sent)), _a(rng.choice(ALREADY_RIGHT_REPLIES).format(s=sent))])
    return out


# ──────────────── 5. several questions / repeated question ────────────────
MULTI: List[Tuple[List[str], List[str]]] = [
    (["What's your name and what can you do?", "who are you and what do you do?", "hi! what are you, and how can you help?"],
     ["I'm Hibari Koto, a small AI. I can chat with you, listen, and help with simple questions and writing.",
      "My name is Hibari Koto. I'm a small AI, and I can chat, answer simple questions and help rewrite sentences."]),
    (["How are you? And what are you up to?", "hey how r u, what's up?", "How are you doing, and what's new?"],
     ["I'm doing well, thanks! I'm just here and ready to chat. How about you?",
      "I'm good, thank you! Nothing much, just happy to talk. What's new with you?"]),
    (["Who made you and when?", "who created you and why?"],
     ["I was made by Kavimugil Rajasekar as a small conversational AI. I don't know the exact date I was finished.",
      "Kavimugil Rajasekar built me to be a friendly conversation partner. I'm not sure of the exact date."]),
    (["Are you a human? Can you see me?", "are you real and can you hear me?"],
     ["No, I'm an AI, not a person. And no, I can't see or hear you, I only read what you type.",
      "I'm a small AI, not a human, and I can only read the messages you type."]),
]
REPEATABLE: List[Tuple[str, str, str]] = [
    ("What's your name?", "I'm Hibari Koto.", "Like I said, I'm Hibari Koto. Is there anything I can help you with?"),
    ("Who made you?", "I was made by Kavimugil Rajasekar.", "As I mentioned, Kavimugil Rajasekar made me."),
    ("Are you a robot?", "I'm an AI, a small language model, not a person.", "Yes, I'm still an AI! I'm a small language model, not a person."),
    ("Can you browse the internet?", "No, I can't access the internet.", "No, I still can't access the internet, sorry. I only know what I learned in training."),
]


def multi_and_repeat_conversations(rng: random.Random) -> List[Conv]:
    out: List[Conv] = []
    for users, replies in MULTI:
        for u in users:
            for r in replies:
                out.append([_u(u), _a(r)])
    for q, a1, a2 in REPEATABLE:
        for _ in range(4):
            conv = [_u(q), _a(a1)]
            fu, fa = rng.choice(FILLERS)
            if rng.random() < 0.5:
                conv += [_u(fu), _a(fa)]
            conv += [_u(rng.choice([q, q.lower(), q.rstrip("?") + " again?"])), _a(a2)]
            out.append(conv)
    return out


# ───────────────────────── entry point ─────────────────────────
FAMILIES = ("recall", "clarify", "honesty", "chat_vs_correction", "multi_repeat")


def build_dialogue_skill_conversations(seed: int = 112, recall_n: int = 1500) -> Dict[str, List[Conv]]:
    """Conversations per family (no system turn)."""
    rng = random.Random(seed)
    return {
        "recall": recall_conversations(rng, recall_n),
        "clarify": clarification_conversations(rng),
        "honesty": honesty_conversations(rng),
        "chat_vs_correction": chat_vs_correction_conversations(rng),
        "multi_repeat": multi_and_repeat_conversations(rng),
    }
