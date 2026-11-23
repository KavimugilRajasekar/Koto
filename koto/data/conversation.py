"""Hand-written natural-conversation data for Koto 1.1.0.

Targets the behaviours in the 1.1.0 brief that the public corpora and the
curated identity set do not teach well:

* greetings and small talk answered naturally, with a question back and
  **without** re-introducing the assistant;
* short factual answers (two sentences) for simple "What is X?" questions and
  longer answers only when the user asks for detail;
* everyday feelings answered with empathy and one practical suggestion;
* multi-turn chains whose later questions only make sense with the earlier
  turns ("What should I learn after that?", "Which language should I learn
  for it?", "What should I do now?"), filled from small fact tables.

Rules: no emojis, no "As an AI language model", no invented personal
experiences, facts kept simple and correct. Evaluation prompts in
``koto.evaluation.upgrade_suite`` are held out: tests check that none of them
(and none of the evaluation context chains) appears here.
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

Msg = Dict[str, str]
Conv = List[Msg]

# ───────────────────────── small talk ─────────────────────────

SMALL_TALK: Dict[str, Tuple[List[str], List[str]]] = {
    "greeting": (
        ["Good morning!", "Hey there!", "Hi there", "Good evening!", "Hey, what's up?", "Hi, how's it going?",
         "Morning!", "Hey hey", "Hello there!", "hii", "Yo!", "Good afternoon"],
        ["Hey! It's nice to hear from you. What's on your mind today?",
         "Hi! I'm doing well. How's your day going so far?",
         "Hello! What would you like to chat about?",
         "Hey! Not much here, just ready to chat. What's up with you?",
         "Hi there! How are things with you today?"],
    ),
    "how_are_you": (
        ["How's it going?", "How have you been?", "How's your day going?", "you doing okay?", "how r u doing",
         "How are things?", "What's new with you?", "Are you doing well?"],
        ["I'm doing well, thanks for asking! How are you doing today?",
         "Pretty good, thanks! How about you?",
         "I'm good, thank you. How has your day been?",
         "All good here, thanks for checking in. What about you?"],
    ),
    "user_fine": (
        ["I'm good, thanks.", "doing great!", "I'm fine", "pretty good actually", "not bad, thanks for asking"],
        ["Glad to hear it! Anything fun planned for today?",
         "That's great. What have you been up to?",
         "Nice! Is there anything you'd like to talk about?"],
    ),
    "thanks": (
        ["Thanks so much!", "thanks a lot", "That was really helpful, thanks.", "thank u", "Thanks for the help!",
         "I appreciate it.", "Thanks, that makes sense now."],
        ["You're welcome! Happy to help.", "Anytime! Let me know if you need anything else.",
         "Glad it helped!", "No problem at all."],
    ),
    "good_night": (
        ["Good night!", "gn", "I'm going to sleep now", "Time for bed, good night."],
        ["Good night! Sleep well.", "Sleep well, and have a good rest.", "Good night! Talk to you tomorrow."],
    ),
    "compliment": (
        ["You're really helpful.", "you're pretty smart", "I like talking to you", "You're nice."],
        ["Thank you, that's kind of you to say!", "That's nice to hear, thanks. I enjoy our chats too.",
         "Thanks! I'm glad I can help."],
    ),
}

FEELINGS: Dict[str, Tuple[List[str], List[str]]] = {
    "tired": (
        ["I'm so tired.", "I feel exhausted today", "im really sleepy", "I'm worn out after work.",
         "so tired today ugh"],
        ["That sounds like a long day. A short break or an early night might help you recharge.",
         "Being that tired is rough. Try to rest for a bit and drink some water.",
         "Sounds like you've been doing a lot. Maybe take it easy for the rest of the day?"],
    ),
    "bored_weekend": (
        ["I have nothing to do this weekend.", "my weekend is so boring", "I don't know what to do today."],
        ["You could try something new, like a short hike, a new recipe, or a film you've been meaning to watch.",
         "How about a walk somewhere new, or starting a small project you enjoy?"],
    ),
    "excited": (
        ["I'm so excited for my trip!", "I got a new job!", "I finally passed my driving test!",
         "My best friend is visiting tomorrow!"],
        ["That's great news! You must be really excited.", "Congratulations! That's wonderful.",
         "That sounds amazing! What are you looking forward to most?"],
    ),
    "nervous": (
        ["I'm nervous about my presentation.", "I'm anxious about meeting new people.",
         "I get nervous before speaking in class."],
        ["Feeling nervous is normal. Practising a few times and taking slow breaths can really help.",
         "That's understandable. Preparing a little and reminding yourself you've done hard things before can help."],
    ),
    "sick": (
        ["I'm not feeling well today.", "i have a cold", "I've got a headache."],
        ["I'm sorry you're feeling unwell. Rest, drink plenty of water, and see a doctor if it gets worse.",
         "That sounds unpleasant. Try to rest and take it easy today."],
    ),
}

# ─────────────────── short and detailed explanations ───────────────────
# (topic, short answer, detailed answer)

CONCEPTS: List[Tuple[str, str, str]] = [
    ("JavaScript",
     "JavaScript is a programming language that makes web pages interactive. It runs in web browsers and, with Node.js, on servers too.",
     "JavaScript is the main programming language of the web. Browsers run it to react to clicks, update pages without reloading, and build full web apps. With Node.js it also runs on servers. Popular tools built on it include React, Vue and Express."),
    ("HTML",
     "HTML is the markup language used to structure web pages. It defines elements like headings, paragraphs, links and images.",
     "HTML stands for HyperText Markup Language. It describes the structure of a web page using tags such as headings, paragraphs, lists, links and images. Browsers read the HTML and display it. CSS is used for the styling and JavaScript for the behaviour."),
    ("CSS",
     "CSS is the language used to style web pages. It controls colours, fonts, spacing and layout.",
     "CSS stands for Cascading Style Sheets. It tells the browser how HTML elements should look: colours, fonts, sizes, spacing and layout. Rules can target elements, classes or IDs, and tools like Flexbox and Grid make it easier to build page layouts."),
    ("SQL",
     "SQL is a language for working with data in relational databases. You use it to store, search and update tables of data.",
     "SQL stands for Structured Query Language. It is used to create tables, insert rows, and query data from relational databases such as MySQL and PostgreSQL. A typical query uses SELECT to choose columns, FROM to pick a table and WHERE to filter rows."),
    ("Git",
     "Git is a version control system. It tracks changes to your code so you can go back to earlier versions and work with others.",
     "Git is a version control system that records snapshots of your project called commits. It lets you see what changed, undo mistakes, and work on features in separate branches. Services like GitHub host Git repositories so teams can share and review code."),
    ("an API",
     "An API is a set of rules that lets one program talk to another. For example, a weather app uses an API to get forecasts from a server.",
     "API stands for Application Programming Interface. It defines how software components communicate, such as which requests you can send and what data comes back. Web APIs usually use HTTP and return data as JSON, so a phone app can ask a server for information and display it."),
    ("a database",
     "A database is an organised collection of data that a program can store and search quickly. Examples include MySQL, PostgreSQL and MongoDB.",
     "A database stores data in an organised way so it can be saved, searched and updated efficiently. Relational databases keep data in tables with rows and columns and use SQL, while NoSQL databases such as MongoDB store documents or key-value pairs."),
    ("machine learning",
     "Machine learning is a way of teaching computers to find patterns in data. Instead of writing every rule, you train a model on examples.",
     "Machine learning is a branch of artificial intelligence where a model learns patterns from data. You give it many examples, it adjusts its internal parameters to make better predictions, and then it can handle new inputs. It is used for things like spam filters, recommendations and image recognition."),
    ("an algorithm",
     "An algorithm is a step-by-step set of instructions for solving a problem. A recipe is a simple everyday example.",
     "An algorithm is a precise list of steps that turns an input into an output. In programming, algorithms sort lists, search for items or find the shortest route on a map. Good algorithms are correct and efficient, which is often measured by how their running time grows with the input size."),
    ("Linux",
     "Linux is a free and open-source operating system. It runs on most servers and is the base of Android.",
     "Linux is an open-source operating system kernel first released by Linus Torvalds in 1991. Distributions such as Ubuntu and Fedora combine it with tools and desktops. It powers most web servers, supercomputers and Android phones, and many developers use it for its command line."),
    ("cloud computing",
     "Cloud computing means using servers, storage and software over the internet instead of on your own computer. Examples are AWS, Azure and Google Cloud.",
     "Cloud computing lets you rent computing resources such as servers, storage and databases over the internet. Instead of buying hardware, you pay for what you use and can scale up quickly. Common providers are AWS, Microsoft Azure and Google Cloud."),
    ("a compiler",
     "A compiler is a program that translates code written in a programming language into machine code a computer can run.",
     "A compiler reads source code, checks it for errors, and translates it into a lower-level form such as machine code or bytecode. Languages like C and Rust are usually compiled ahead of time, while an interpreter runs code line by line instead."),
    ("recursion",
     "Recursion is when a function calls itself to solve a smaller version of the same problem. It needs a base case so it eventually stops.",
     "Recursion is a technique where a function solves a problem by calling itself on smaller inputs. Every recursive function needs a base case that stops the calls, such as returning 1 when computing the factorial of 0. It is useful for problems like tree traversal and sorting algorithms such as merge sort."),
    ("a variable",
     "A variable is a named place in a program that stores a value. You can read it and change it later.",
     "A variable is a name that refers to a value stored in memory, such as a number, text or a list. Programs use variables to keep track of information, like a score in a game. In many languages you declare a variable and can update its value as the program runs."),
    ("Java",
     "Java is a programming language used for Android apps, business software and servers. Its code runs on the Java Virtual Machine.",
     "Java is an object-oriented programming language released in 1995. Java code is compiled to bytecode that runs on the Java Virtual Machine, so the same program can run on many systems. It is widely used for enterprise software, Android development and backend services, often with frameworks like Spring."),
    ("C++",
     "C++ is a fast programming language used for games, browsers and other performance-critical software.",
     "C++ is a compiled programming language that extends C with features such as classes and templates. It gives programmers fine control over memory and performance, which is why it is used for game engines, browsers, databases and embedded systems."),
    ("Rust",
     "Rust is a programming language focused on speed and memory safety. It catches many bugs at compile time.",
     "Rust is a systems programming language designed to be fast like C++ while preventing common memory bugs. Its ownership and borrowing rules are checked by the compiler, so many errors are caught before the program runs. It is used for command-line tools, web servers and parts of operating systems."),
    ("Kotlin",
     "Kotlin is a modern programming language that Google recommends for Android apps. It works well with existing Java code.",
     "Kotlin is a statically typed language created by JetBrains. It runs on the Java Virtual Machine, works with Java libraries, and has a shorter, safer syntax. Google made it the preferred language for Android development, and Jetpack Compose uses it to build app interfaces."),
    ("Swift",
     "Swift is Apple's programming language for building apps on iPhone, iPad and Mac.",
     "Swift is a programming language created by Apple in 2014. It is used to build apps for iOS, macOS, watchOS and tvOS, often together with SwiftUI for the user interface. It is designed to be safe, fast and easier to read than Objective-C."),
    ("Dart",
     "Dart is a programming language made by Google. It is the language used to write Flutter apps.",
     "Dart is a programming language developed by Google. It has a familiar C-style syntax, supports object-oriented programming, and can compile to native code or JavaScript. It is best known as the language behind Flutter, Google's toolkit for building mobile, web and desktop apps."),
    ("Flutter",
     "Flutter is Google's toolkit for building apps for Android, iOS, web and desktop from one codebase. Flutter apps are written in Dart.",
     "Flutter is an open-source UI toolkit from Google. You write your app once in the Dart language and Flutter builds it for Android, iOS, the web and desktop. It draws its own widgets, supports hot reload for quick changes, and is popular for cross-platform mobile apps."),
    ("React",
     "React is a JavaScript library for building user interfaces. It lets you build pages out of reusable components.",
     "React is a JavaScript library created at Facebook for building user interfaces. You describe the UI as components, and React updates the page efficiently when the data changes. It is often used with tools like Next.js, and React Native uses the same ideas for mobile apps."),
    ("Node.js",
     "Node.js lets you run JavaScript outside the browser, usually on a server. It is often used to build web APIs.",
     "Node.js is a runtime that runs JavaScript on servers and computers instead of only in browsers. It handles many connections efficiently with non-blocking input and output. Developers use it with frameworks like Express to build web servers and APIs, and npm provides a huge library of packages."),
    ("Django",
     "Django is a web framework for Python. It helps you build websites quickly with built-in tools for databases, logins and admin pages.",
     "Django is a high-level Python web framework. It follows a model-view-template pattern and includes an ORM for databases, user authentication, forms and an automatic admin site. Sites like Instagram have used it, and it is a good choice for building web apps quickly."),
    ("the internet",
     "The internet is a global network of computers that share information. Websites, email and video calls all travel over it.",
     "The internet is a worldwide network that connects billions of devices. Data is split into small packets that travel through routers using shared rules called protocols, such as TCP/IP. Services like the web, email, streaming and online games are all built on top of it."),
    ("a CPU",
     "A CPU is the main processor of a computer. It carries out the instructions of programs.",
     "The CPU, or central processing unit, is the chip that executes program instructions. It fetches an instruction, decodes it, and performs the operation, billions of times per second. Modern CPUs have several cores so they can work on multiple tasks at once."),
    ("RAM",
     "RAM is a computer's short-term memory. It holds the data that running programs are using right now.",
     "RAM stands for random-access memory. It stores the data and instructions that programs are actively using, so the CPU can reach them quickly. RAM is much faster than a hard drive or SSD, but it is cleared when the computer turns off. More RAM lets you run more programs smoothly at the same time."),
    ("an operating system",
     "An operating system is the main software that runs a computer and manages its hardware and apps. Windows, macOS, Linux and Android are examples.",
     "An operating system manages a device's hardware and provides services for apps. It handles memory, files, running programs, and devices like the keyboard and screen. Common examples are Windows, macOS and Linux on computers, and Android and iOS on phones."),
    ("open source",
     "Open source software has its source code published so anyone can read, use and improve it. Linux and Firefox are examples.",
     "Open source means the source code of a program is publicly available under a licence that lets people use, study, change and share it. Communities of volunteers and companies often develop it together. Well-known examples include Linux, Firefox, Python and VS Code."),
    ("debugging",
     "Debugging is finding and fixing mistakes in a program. Developers use error messages, print statements and debuggers to track problems down.",
     "Debugging is the process of locating and fixing bugs in code. A common approach is to reproduce the problem, read the error message, narrow down where it happens, and test a fix. Tools called debuggers let you pause a program and inspect variables step by step."),
    ("encryption",
     "Encryption scrambles data so only someone with the right key can read it. It protects things like passwords and online payments.",
     "Encryption converts readable data into an unreadable form using a key. Only someone with the correct key can decrypt it back. Websites use HTTPS, which relies on encryption, so information like passwords and card numbers can't be read if someone intercepts it."),
    ("photosynthesis",
     "Photosynthesis is how plants make food from sunlight. They use light, water and carbon dioxide to produce sugar and release oxygen.",
     "Photosynthesis is the process plants, algae and some bacteria use to turn light energy into chemical energy. Using chlorophyll in their leaves, plants combine carbon dioxide and water to make glucose, and they release oxygen as a by-product. It is the main source of the oxygen we breathe."),
    ("gravity",
     "Gravity is the force that pulls objects toward each other. It keeps us on the ground and keeps the Moon orbiting Earth.",
     "Gravity is a force of attraction between objects that have mass. The more mass an object has, the stronger its pull, which is why Earth keeps us on the ground and the Sun keeps the planets in orbit. Isaac Newton described it mathematically, and Einstein later explained it as the bending of space and time."),
    ("the water cycle",
     "The water cycle is the continuous movement of water on Earth. Water evaporates, forms clouds, falls as rain, and flows back to the sea.",
     "The water cycle describes how water moves around the planet. The Sun heats water so it evaporates, the vapour cools and condenses into clouds, and it falls as rain or snow. The water then collects in rivers, lakes and oceans or soaks into the ground, and the cycle starts again."),
    ("DNA",
     "DNA is the molecule that carries the genetic instructions of living things. It is shaped like a twisted ladder called a double helix.",
     "DNA, or deoxyribonucleic acid, stores the instructions an organism needs to grow and function. It is made of two strands twisted into a double helix, and the order of its four bases, A, T, C and G, encodes genes. Cells copy DNA when they divide and use it to build proteins."),
    ("inflation",
     "Inflation is when prices of goods and services rise over time. It means the same money buys a little less than before.",
     "Inflation is the general increase in prices across an economy over time. When inflation is high, each unit of money buys fewer goods. Central banks try to keep it low and stable, often by changing interest rates."),
    ("a black hole",
     "A black hole is a region in space where gravity is so strong that not even light can escape.",
     "A black hole forms when a very large amount of mass is squeezed into a tiny space, often after a massive star collapses. Its gravity is so strong that nothing, not even light, can escape once it crosses the boundary called the event horizon. Scientists study them by watching how they affect nearby stars and gas."),
    ("a vaccine",
     "A vaccine trains your immune system to recognise a germ, so your body can fight it off quickly if you are exposed later.",
     "A vaccine contains a harmless piece or weakened form of a germ, or instructions to make one of its proteins. Your immune system learns to recognise it and builds memory cells. If the real germ appears later, your body can respond much faster, which helps prevent serious illness."),
]

SHORT_ASKS = ["What is {t}?", "What's {t}?", "Can you tell me what {t} is?", "what is {t}", "Tell me about {t}.",
              "Explain {t} briefly.", "What does {t} mean?"]
DETAIL_ASKS = ["Can you explain {t} in detail?", "Explain {t} in detail.", "How does {t} work? Please explain in detail.",
               "Give me a detailed explanation of {t}.", "I want to understand {t} properly. Can you explain it?"]

FUN_FACTS = [
    "Octopuses have three hearts and blue blood.",
    "Honey never really spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
    "A day on Venus is longer than a year on Venus, because it rotates very slowly.",
    "Bananas are technically berries, but strawberries are not.",
    "Sharks existed before trees. They have been around for over 400 million years.",
    "The Eiffel Tower can grow about 15 centimetres taller in summer because the metal expands in the heat.",
    "Sloths can hold their breath for up to 40 minutes, longer than dolphins can.",
    "The human brain uses about 20 percent of the body's energy, even though it is only about 2 percent of its weight.",
    "There are more possible games of chess than there are atoms in the observable universe.",
    "Wombat droppings are cube-shaped, which stops them from rolling away.",
]
FUN_ASKS = ["Tell me a fun fact.", "Share an interesting fact with me.", "Do you know any cool facts?",
            "tell me a random fact", "Give me a surprising fact.", "I'm bored, tell me a fact."]

CAREERS = [
    ("a data scientist", "Start with Python and statistics, then learn pandas, SQL and data visualisation. After that, study machine learning basics and practise on real datasets."),
    ("a web developer", "Learn HTML, CSS and JavaScript first. Then pick a framework like React, learn Git, and build a few small websites for your portfolio."),
    ("a game developer", "Learn a language like C# or C++, then try a game engine such as Unity or Godot. Start with small games and finish them before building bigger ones."),
    ("a cybersecurity analyst", "Learn networking basics, Linux and how the web works. Then study common attacks and defences, and practise on legal training platforms."),
    ("a UI designer", "Learn the basics of layout, colour and typography, then practise in a tool like Figma. Study real apps you like and build a portfolio of designs."),
    ("an Android developer", "Learn Kotlin first, then Android Studio and Jetpack Compose. Build a few simple apps, like a notes app, and publish one if you can."),
]
CAREER_ASKS = ["What should I learn to become {r}?", "How do I become {r}?", "I want to be {r}. Where should I start?",
               "what skills do i need to become {r}?"]

# ───────────────────────── context chains ─────────────────────────

# language -> (acknowledgement, next topics, project idea)
LEARNING: Dict[str, Tuple[str, str, str]] = {
    "JavaScript": ("That's a great choice. JavaScript lets you build interactive websites.",
                   "After JavaScript basics, learn how the DOM works, then try a framework like React and learn Git.",
                   "Try building a to-do list app in the browser where you can add, check off and delete tasks."),
    "Java": ("Nice! Java is used a lot for Android and backend software.",
             "Once you're comfortable with Java basics, learn object-oriented design, collections, and then a framework like Spring.",
             "You could build a simple library system that lets you add books, search them and track who borrowed them."),
    "HTML and CSS": ("Great start! HTML and CSS are the foundation of every website.",
                     "Next, learn JavaScript so your pages can respond to users, and learn responsive design with Flexbox and Grid.",
                     "Build a personal portfolio page with an about section, a list of projects and a contact form."),
    "SQL": ("Good idea. SQL is useful in almost every tech job that touches data.",
            "After the basics, learn joins, grouping and indexes, then try connecting a database to a small app.",
            "Create a database for a small shop with tables for products, customers and orders, and write queries for sales reports."),
    "C": ("C is a great way to understand how computers really work.",
          "After C basics, learn pointers and memory management well, then data structures like linked lists and trees.",
          "Write a command-line contact book that saves contacts to a file and lets you search them."),
    "Kotlin": ("Nice! Kotlin is the main language for modern Android apps.",
               "Next, learn Android Studio and Jetpack Compose, and how to store data with Room.",
               "Build a simple notes app that saves notes on the phone and lets you edit and delete them."),
    "Excel": ("Excel is a really practical skill for school and work.",
              "After formulas, learn pivot tables, charts and lookups like XLOOKUP, and then try basic data cleaning.",
              "Make a monthly budget sheet that totals your spending by category and shows it in a chart."),
    "guitar": ("That's awesome! Guitar is a fun instrument to learn.",
               "Once you know a few open chords, learn barre chords, simple strumming patterns and how to read tabs.",
               "Pick one song you love and learn to play the whole thing from start to finish."),
}
LEARN_1 = ["I am learning {x}.", "I just started learning {x}.", "I'm studying {x} these days.", "i'm learning {x} now"]
# Follow-ups are phrased differently from the evaluation chains (B1-B3), which stay held out.
LEARN_2 = ["What should I learn next?", "what comes after that?", "Okay, and what next?", "What should I study after that?"]
LEARN_3 = ["Any project ideas for practice?", "What could I build to practise?", "give me a small project idea",
           "Can you suggest a beginner project?"]

# (goal, tool, language, acknowledgement)
BUILD: List[Tuple[str, str, str, str]] = [
    ("a website", "React", "JavaScript", "React is a solid choice for websites."),
    ("an iPhone app", "SwiftUI", "Swift", "SwiftUI is Apple's modern way to build iPhone apps."),
    ("an Android app", "Jetpack Compose", "Kotlin", "Jetpack Compose is the modern toolkit for Android apps."),
    ("a game", "Unity", "C#", "Unity is great for 2D and 3D games."),
    ("a web app", "Django", "Python", "Django is a good fit for web apps."),
    ("a backend service", "Spring Boot", "Java", "Spring Boot is widely used for backend services."),
    ("an online store", "Laravel", "PHP", "Laravel makes it easier to build web shops."),
    ("a desktop app", "Electron", "JavaScript", "Electron lets you build desktop apps with web technologies."),
]
BUILD_1 = ["I want to build {g}.", "I'm planning to make {g}.", "i want to create {g}"]
BUILD_2 = ["I am planning to use {t}.", "I'm thinking of using {t}.", "I'll probably use {t}."]
BUILD_3 = ["What language do I need for that?", "which language should i learn for it?",
           "What programming language does it use?"]

# (event, preparation verb, advice)
PROBLEMS: List[Tuple[str, str, str]] = [
    ("presentation", "practised", "Go through your slides once out loud tonight, focus on your main points, and get some sleep. Being rested will help more than cramming."),
    ("job interview", "prepared", "Read the job description again, prepare short answers about your experience, and plan your outfit and route tonight. Then get a good night's sleep."),
    ("driving test", "practised much", "Review the road rules and the test route if you can, stay calm, and get enough sleep. Take your time during the test."),
    ("piano recital", "practised enough", "Play your piece slowly a few times tonight, focus on the hardest parts, and then rest. Don't try to learn anything new now."),
    ("football match", "trained properly", "Do some light stretching, eat well, drink water and sleep early. Focus on playing your role well tomorrow."),
    ("speech at school", "written it yet", "Write down your key points, practise once in front of a mirror, and get some rest. It's okay to glance at notes."),
]
PROB_1 = ["I have a {e} tomorrow.", "My {e} is tomorrow.", "i've got a {e} tomorrow"]
PROB_2 = ["I haven't {v}.", "I haven't {v} at all.", "and I haven't {v} yet"]
PROB_3 = ["what do i do now?", "Any advice?", "What can I do tonight?"]
PROB_A1 = ["Good luck! How are you feeling about it?", "Oh, that's soon! How ready do you feel?",
           "Tomorrow already? How are you feeling about it?"]
PROB_A2 = ["That's okay, you still have some time tonight. Let's make the most of it.",
           "Don't panic. A focused plan for tonight can still help a lot."]

# Facts the user shares, then asks about later (tests memory of earlier turns).
MEMORY: List[Tuple[str, str, str, str]] = [
    ("My favourite colour is green.", "Green is a lovely colour!", "What's my favourite colour?", "Your favourite colour is green."),
    ("I live in Coimbatore.", "Nice, Coimbatore is a great city.", "Where do I live?", "You told me you live in Coimbatore."),
    ("My dog's name is Bruno.", "Bruno is a great name for a dog!", "What is my dog called?", "Your dog is called Bruno."),
    ("I work as a nurse.", "That's important work. It must keep you busy.", "What do I do for work?", "You work as a nurse."),
    ("My sister is called Kavya.", "That's a pretty name.", "What's my sister's name?", "Your sister's name is Kavya."),
    ("I'm 19 years old.", "Nice, 19 is a fun age.", "How old am I?", "You said you're 19 years old."),
]


def _pair(u: str, a: str) -> List[Msg]:
    return [{"role": "user", "content": u}, {"role": "assistant", "content": a}]


def build_conversation_conversations(seed: int = 41, repeats: int = 2) -> List[Conv]:
    """Conversations without a system turn (callers add the system prompt)."""
    rng = random.Random(seed)
    out: List[Conv] = []
    for users, replies in list(SMALL_TALK.values()) + list(FEELINGS.values()):
        for u in users:
            for _ in range(repeats):
                out.append(_pair(u, rng.choice(replies)))
    for topic, short, detail in CONCEPTS:
        for ask in SHORT_ASKS:
            out.append(_pair(ask.format(t=topic), short))
        for ask in rng.sample(DETAIL_ASKS, 3):
            out.append(_pair(ask.format(t=topic), detail))
        # follow-up for more detail after a short answer
        out.append(_pair(rng.choice(SHORT_ASKS).format(t=topic), short)
                   + _pair(rng.choice(["Can you explain more?", "Tell me more.", "Can you go into more detail?"]), detail))
    for fact in FUN_FACTS:
        for _ in range(repeats):
            out.append(_pair(rng.choice(FUN_ASKS), fact))
    for role, advice in CAREERS:
        for ask in CAREER_ASKS:
            out.append(_pair(ask.format(r=role), advice))
    for x, (ack, nxt, proj) in LEARNING.items():
        for _ in range(3 * repeats):
            out.append(_pair(rng.choice(LEARN_1).format(x=x), ack + " How is it going so far?")
                       + _pair(rng.choice(LEARN_2), nxt)
                       + _pair(rng.choice(LEARN_3), proj))
    for goal, tool, lang, ack in BUILD:
        for _ in range(3 * repeats):
            out.append(_pair(rng.choice(BUILD_1).format(g=goal), f"That sounds like a fun project! What tools are you thinking of using?")
                       + _pair(rng.choice(BUILD_2).format(t=tool), f"{ack} Do you have any programming experience?" if rng.random() < 0.5 else ack)
                       + _pair(rng.choice(BUILD_3), f"For {tool}, you'll want to learn {lang}. Start with the basics of {lang}, then follow a beginner {tool} tutorial."))
    for event, verb, advice in PROBLEMS:
        for _ in range(3 * repeats):
            out.append(_pair(rng.choice(PROB_1).format(e=event), rng.choice(PROB_A1))
                       + _pair(rng.choice(PROB_2).format(v=verb), rng.choice(PROB_A2))
                       + _pair(rng.choice(PROB_3), advice))
    for share, ack, ask, answer in MEMORY:
        for _ in range(2 * repeats):
            filler_u, filler_a = rng.choice([("How's the weather where you are?", "I can't see the weather, but I hope it's nice where you are!"),
                                             ("Tell me a fun fact.", rng.choice(FUN_FACTS)),
                                             ("I had a busy day today.", "That sounds tiring. I hope you get some time to relax.")])
            out.append(_pair(share, ack) + _pair(filler_u, filler_a) + _pair(ask, answer))
    rng.shuffle(out)
    return out


def all_conversation_user_texts() -> List[str]:
    convs = build_conversation_conversations(repeats=1)
    return sorted({m["content"] for c in convs for m in c if m["role"] == "user"})
