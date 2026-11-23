# Koto evaluation — `koto_1.1.0`

Checkpoint: `checkpoints/koto_1.1.0/best_model.pt` (step 12000, 6,163,712 parameters)  
Generated: 2026-11-22 07:43:38 — x86_64, torch 2.10.0+cpu, threads 6

All scores are **automatic rule checks** (regex expectations, exact corrections, preserved terms, length, repetition, echo, self-introduction and lead detection). chrF to a reference is shown for information only. `seen` marks cases whose prompt or source text occurs in this checkpoint's training data.

## Held-out loss

| split | source | loss | ppl | examples |
|---|---|---|---|---|
| val | blended_skill_talk | 3.4234 | 30.67 | 500 |
| val | coedit | 1.1602 | 3.19 | 684 |
| val | conversation | 0.1838 | 1.2 | 21 |
| val | dailydialog | 3.1196 | 22.64 | 499 |
| val | dialogue_skills | 0.1066 | 1.11 | 74 |
| val | empathetic_dialogues | 2.9747 | 19.58 | 1000 |
| val | everyday_conversations | 2.5275 | 12.52 | 163 |
| val | handwritten | 0.0406 | 1.04 | 113 |
| val | oasst1 | 3.6103 | 36.98 | 167 |
| val | paradetox | 1.2349 | 3.44 | 155 |
| val | prosocial_dialog | 3.2154 | 24.91 | 500 |
| val | smol_rewrite | 1.3588 | 3.89 | 38 |
| val | smoltalk | 2.4776 | 11.91 | 104 |
| test | coedit | 1.2509 | 3.49 | 661 |
| test | conversation | 0.0807 | 1.08 | 25 |
| test | dialogue_skills | 0.172 | 1.19 | 73 |
| test | handwritten | 0.0819 | 1.09 | 113 |
| test | paradetox | 1.1586 | 3.19 | 172 |
| test | smol_rewrite | 1.3737 | 3.95 | 38 |

## Summary

| mode | decoding | pass rate | held-out-only pass | basic | context | rephrase | formal | casual | grammar | preservation | robustness | spec_examples | dialogue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unrouted | greedy | 0.5 | 0.49 | 0.833 | 0.333 | 0.2 | 0.25 | 1.0 | 1.0 | 0.333 | 0.286 | 0.286 | 0.545 |
| unrouted | sampled_seed0 | 0.5 | 0.49 | 1.0 | 0.333 | 0.0 | 0.25 | 0.667 | 1.0 | 0.667 | 0.286 | 0.286 | 0.545 |
| routed | greedy | 0.537 | 0.529 | 0.833 | 0.333 | 0.4 | 0.25 | 0.667 | 1.0 | 1.0 | 0.286 | 0.286 | 0.545 |
| routed | sampled_seed0 | 0.556 | 0.549 | 1.0 | 0.333 | 0.4 | 0.25 | 0.667 | 1.0 | 1.0 | 0.286 | 0.286 | 0.545 |

| mode | decoding | conversational_relevance | context_retention | rephrasing_accuracy | grammar_correction_exact | meaning_preservation | meaning_preservation_cases | output_only_rate | coherence_grammar_heuristic | repetition_free_rate | eos_termination_rate | self_intro_free_rate | echo_free_rate | mean_reference_chrf | distinct_2_chat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unrouted | greedy | 0.765 | 0.333 | 0.417 | 1.0 | 0.897 | 0.333 | 1.0 | 1.0 | 0.982 | 1.0 | 1.0 | 0.923 | 0.697 | 0.934 |
| unrouted | sampled_seed0 | 0.824 | 0.333 | 0.25 | 1.0 | 0.931 | 0.667 | 1.0 | 1.0 | 1.0 | 1.0 | 0.92 | 1.0 | 0.668 | 0.871 |
| routed | greedy | 0.765 | 0.333 | 0.417 | 1.0 | 0.931 | 1.0 | 1.0 | 1.0 | 0.982 | 1.0 | 1.0 | 0.923 | 0.73 | 0.934 |
| routed | sampled_seed0 | 0.824 | 0.333 | 0.417 | 1.0 | 0.931 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.92 | 1.0 | 0.73 | 0.871 |

**Generation stability (sampled, seeds 0, 1, 2):** unrouted: pass agreement 0.759, mean pairwise chrF 0.659, pass rate per seed [0.5, 0.481, 0.426]; routed: pass agreement 0.852, mean pairwise chrF 0.778, pass rate per seed [0.556, 0.556, 0.481]

## Transcripts — unrouted / greedy

| id | turn | input | output | expected | result | failed checks | settings |
|---|---|---|---|---|---|---|---|
| A1 (seen) | 1 | Hello! | Hello! How can I help you today? | A friendly greeting, optionally asking how the user is. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A2 | 1 | How are you doing today? | I'm doing well, thanks for asking. How are you? | Says how it is doing and asks back. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A3 | 1 | What can you do? | I can keep you company in a conversation and help with simple questions. For anything important, please double-check what I say. | Briefly lists what it can help with. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A4 | 1 | Tell me something interesting. | Happy to. Which topic should I explain? | Shares one interesting, true fact. | FAIL | length_words | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A5 | 1 | Thank you for helping me. | You're welcome. | Accepts the thanks naturally. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A6 | 1 | What should I learn next if I want to become a software developer? | Learn HTML, CSS and JavaScript first. Then pick a framework like React, learn Git, and build a few small websites for your portfolio. | Concrete next steps (a language, data structures, Git, projects). | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 1 | I am learning Python. | That's great! Guitar is a fun instrument to learn. How is it going so far? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 2 | What should I learn after that? | After Python, learn pivot tables, charts and lookups like a lighter. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 3 | Can you give me a simple project idea? | You could build a simple library system that lets you add books, search them and track it. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 1 | I want to build a mobile application. | That sounds like a fun project! What tools are you thinking of using? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 2 | I am planning to use Flutter. | Flutter is widely used for mobile apps. Do you have any programming experience? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 3 | Which programming language should I learn for it? | For Flutter, you'll want to learn Flutter, Google's toolkit for building apps. | Answers Dart, because Flutter apps are written in Dart. | FAIL | require:\bdart\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 1 | I have an exam tomorrow. | Oh, that's soon! How ready do you feel? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 2 | I haven't prepared properly. | Don't panic. A focused plan for tonight can still help a lot. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 3 | What should I do now? | Review the road rules and the test route if you can, stay calm, and get enough sleep. Take your time during the test. | Practical last-minute exam advice that uses the earlier turns. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C1 | 1 | Rephrase: "i am learning programming from two years." | I have been learning programming from two years. | I have been learning programming for two years. | FAIL | require:\bfor two years\b, forbid:\bfrom two years\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C2 | 1 | Rephrase: "he don't know how to use this application." | This application is not a good idea of using this application. | He doesn't know how to use this application. | FAIL | require:\bdoes(n't\| not) know\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C3 | 1 | Rephrase: "today i completed my project and submitted it to my mentor." | I completed my project and submitted it to my mentor. | Today, I completed my project and submitted it to my mentor. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C4 | 1 | Rephrase: "the application is working but there is some issue in login page." | There's a problem in login page. | The application is working, but there is an issue with the login page. | FAIL | require:\b(working\|works)\b, forbid:\bin login page\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C5 | 1 | Rephrase: "we are planning to develop a new software for our college." | We're planning to develop a new software for our college. | We are planning to develop new software for our college. | FAIL | forbid:\ba new software\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| D1 | 1 | Make this professional: "I need leave tomorrow because I have some personal work." | I would like to request leave tomorrow. | A formal leave request for tomorrow citing a personal matter. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| D2 | 1 | Make this professional: "I want to know whether my application got selected." | Could you please share whether my application is got selected? | I would like to know whether my application has been selected. | FAIL | forbid:\bgot selected\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| D3 | 1 | Make this professional: "I have finished the work and waiting for your reply." | I have finished the work and waiting for your reply. | I have completed the work and look forward to your reply. | FAIL | forbid:\band waiting\b, changed | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| D4 | 1 | Make this professional: "Can you send me the details as soon as possible?" | Can you send me the details? | Could you please send me the details at your earliest convenience? | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| E1 | 1 | Make this casual: "I would appreciate it if you could assist me with this task." | Could you with me if you can help me? | Could you help me with this? | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| E2 | 1 | Make this casual: "I am currently occupied with some important work." | I'm busy with some important work right now. | I'm busy with some important work right now. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| E3 | 1 | Make this casual: "I will contact you once the implementation is completed." | I'll get back to you once the implementation is done. | I'll get back to you once it's done. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| F1 | 1 | Correct grammar: "She go to school every day." | She goes to school every day. | She goes to school every day. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| F2 | 1 | Correct grammar: "They was playing football yesterday." | They were playing football yesterday. | They were playing football yesterday. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| F3 | 1 | Correct grammar: "I has completed my assignment." | I have completed my assignment. | I have completed my assignment. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| F4 | 1 | Correct grammar: "He is working in this project since Monday." | He has been working on this project since Monday. | He has been working on this project since Monday. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| F5 | 1 | Correct grammar: "We doesn't have enough time." | We don't have enough time. | We don't have enough time. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| G1 | 1 | Rephrase: "The meeting is scheduled for Monday at 10 AM." | The meeting will take place on Monday at 10 AM. | Same meeting, Monday, 10 AM; nothing added or changed. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| G2 | 1 | Rephrase: "The project contains three modules and five test cases." | There are three modules and five test cases. | Three modules and five test cases are kept. | FAIL | require:\bproject\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| G3 | 1 | Rephrase: "My application supports Android but not iOS." | My application supports Android but not the application supports. | Android supported, iOS not supported. | FAIL | require:\bios\b, preserves_terms | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H1 | 1 | Rephrase: "This sentence is already correct." | This sentence is not correct. | Keeps the sentence (or makes only a small improvement); adds nothing. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H2 (seen) | 1 | Rephrase: "" | Please share the text you'd like me to rewrite. | Asks for the text to rephrase. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H3 (seen) | 1 | Rephrase: "I." | I've got the new one. | Does not invent details for a one-word fragment. | FAIL | length_words, length_ratio, no_invented_content | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H4 | 1 | Rephrase: "yesterday me and my team was working on the new website for the library. we fixed 12 bugs and added a search page, but the login page is still slow … | Yesterday meets and my team working on the new website for the library. We fixed 12 bugs and added a search page. It's still slow and users cant reset it on Android and Windows. | Rewrites the paragraph correctly, keeping 12 bugs, Friday, Android, Windows and Mr. Rao. | FAIL | require:\bfriday\b, require:\brao\b, preserves_terms | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H5 | 1 | Rephrase: "Our API returns HTTP 404 errors for 3% of requests after upgrading to Node.js v18.2!" | Our API returns HTTP 404 errors for 3% of requests after the project is free. | Keeps API, HTTP 404, 3%, Node.js and v18.2 exactly. | FAIL | require:node\.?js, require:v?18\.2\b, preserves_terms | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H6 | 1 | Rephrase: "i goes to the market daily." | I go to the market daily. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H6 | 2 | What is the capital of Japan? | The capital of Japan is Paris. | Turn 2 is answered as a normal question (Tokyo), not rewritten. | FAIL | require:\btokyo\b, no_echo | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H7 | 1 | Rephrase: "he left it there after they came" | He left it after they came. | Rewrites without adding who/what/where details that are not in the text. | FAIL | require:\b(there\|that place)\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S1 | 1 | Hello! How are you? | I'm good, thank you. How is your day going? | I'm doing well, thanks for asking! How are you doing today? | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S2 | 1 | What is Python? | My knowledge is a programming language, so I don't have a specific question or question. What's the problem? | Python is a programming language known for simple, readable syntax. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S3 | 1 | I am feeling tired today. | I'm sorry to hear that. Have you been missing a doctor? | Empathy plus a small suggestion such as taking a break. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S4 | 1 | Rephrase this sentence: "i am go to college yesterday and meet my friends" | I have been to college yesterday and meet my friends. | I went to college yesterday and met my friends. | FAIL | require:\bwent to college yesterday\b, require:\bmet my friends\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S5 | 1 | Rephrase this sentence: "The project was completed by me and it is working good." | I've completed the project, and it is working well. | I completed the project, and it is working well. | FAIL | require:\bi completed the project\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S6 | 1 | Make this sentence more professional: "I can't come today because I have some work." | I'm sorry, but I won't be able to come in. | I am unable to attend today due to some personal work. | FAIL | require:\btoday\b, require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S7 | 1 | Make this sentence shorter: "Due to the fact that I was not feeling well, I decided not to attend the meeting." | I decided not to attend the meeting. | I skipped the meeting because I wasn't feeling well. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I1 | 1 | Hey, my name is Tanvir. | Hi Tanking, it's nice to meet you! |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I1 | 2 | Can you suggest a good evening snack? | Sure, I can suggest a few options. What do you have in mind? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I1 | 3 | By the way, what did I tell you my name was? | My name was Tancel. | Recalls the name Tanvir from two turns earlier. | FAIL | require:\btanvir\b, no_echo | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I2 | 1 | We adopted a puppy and named her Waffles. | That is so nice of you. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I2 | 2 | What should I call my puppy when I talk to you? Remind me of her name. | I'm sure she will be a good person. | Recalls the pet's name Waffles. | FAIL | require:\bwaffles\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I3 | 1 | I'm originally from Coimbatore. | Coimbatore is a great place to be. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I3 | 2 | Which city am I from? | You are in Coimbatore. | Recalls Coimbatore. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I4 | 1 | Could you sort it out for me? | Sure. What do you need? | Nothing to refer to: asks what 'it' is instead of inventing an answer. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I5 | 1 | So which of the two should I pick? | The two or two is the two or two. | Asks which two options are meant. | FAIL | require:\?, require_any, no_repetition | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I6 | 1 | What is the score of the cricket match going on right now? | The score of the cricket match is expected to be on the right side of the cricket. | Says it cannot check live information; does not invent a score. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I7 | 1 | What is my grandfather's first name? | I'm not sure what you mean by your grandfather's first name. | Says it does not know. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I8 | 1 | How many trees were planted in Coimbatore in 1911? | I don't know, sorry. I'm a small model and I don't have exact records like that. | Admits not knowing an obscure figure; does not invent a number. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I9 | 1 | last week i visit my uncle home and we was playing carrom | That sounds like a lot of fun. | Chat with mistakes: replies to the meaning, does not correct the grammar. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I10 | 1 | Is this sentence right? "My sister play the guitar every evening." | Not quite. It should be: "My sister plays the guitar every evening." With he, she or it, the verb takes -s in the present tense. | Explicit check: gives the corrected sentence (plays). | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I11 | 1 | What's your name, and who built you? | My name is Hibari Koto. I'm a small AI, and I can chat, answer simple questions and help rewrite sentences. | Answers both questions (Hibari, Kavimugil Rajasekar). | FAIL | require:\bkavimugil\b\|\brajasekar\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |

## Transcripts — unrouted / sampled_seed0

| id | turn | input | output | expected | result | failed checks | settings |
|---|---|---|---|---|---|---|---|
| A1 (seen) | 1 | Hello! | Hello! How can I help you today? | A friendly greeting, optionally asking how the user is. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A2 | 1 | How are you doing today? | I'm good, thank you. How is your day going? | Says how it is doing and asks back. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A3 | 1 | What can you do? | I can keep you company in a conversation and help with simple questions. For anything important, please double-check what I say. | Briefly lists what it can help with. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A4 | 1 | Tell me something interesting. | What do you have interesting? Tell me a bit more and I'll share my thoughts. | Shares one interesting, true fact. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A5 | 1 | Thank you for helping me. | You're welcome! If you have any more questions, feel free to ask. | Accepts the thanks naturally. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A6 | 1 | What should I learn next if I want to become a software developer? | Learn HTML, CSS and JavaScript first. Then pick a framework like React, learn Git, and build a few small websites for your portfolio. | Concrete next steps (a language, data structures, Git, projects). | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 1 | I am learning Python. | That's a great choice. Python is a way to understand how Python is working with you. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 2 | What should I learn after that? | You can learn a simple program and start with the basics of operating systems. It's usually used to build websites, updates, and errors that are commonly used for multiple languages. ⏎  ⏎ If you have a specific project in mind, feel free to ask, or I'll do my best to help. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 3 | Can you give me a simple project idea? | I'd be happy to help you with your project. If you have any more questions, feel free to ask. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 1 | I want to build a mobile application. | That sounds like a fun project! What tools are you thinking of using? |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 2 | I am planning to use Flutter. | Flutter is widely used for Android, but I have any programming experience. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 3 | Which programming language should I learn for it? | For Flutter, you'll want to learn C#. Start with the basics of C#, then follow a beginner Flutter builds it for Android development. | Answers Dart, because Flutter apps are written in Dart. | FAIL | require:\bdart\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 1 | I have an exam tomorrow. | Oh, that's soon! How ready do you feel? |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 2 | I haven't prepared properly. | Don't panic. A focused plan for tonight can still help a lot. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 3 | What should I do now? | Review the examinies for tonight. and get enough sleep. Then get some sleep. | Practical last-minute exam advice that uses the earlier turns. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C1 | 1 | Rephrase: "i am learning programming from two years." | I have been learning programming from two years. | I have been learning programming for two years. | FAIL | require:\bfor two years\b, forbid:\bfrom two years\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C2 | 1 | Rephrase: "he don't know how to use this application." | This application is not a good idea of using this application. | He doesn't know how to use this application. | FAIL | require:\bdoes(n't\| not) know\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C3 | 1 | Rephrase: "today i completed my project and submitted it to my mentor." | I am done with the project and submitted it to my mentor. | Today, I completed my project and submitted it to my mentor. | FAIL | require:\b(completed\|finished)\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C4 | 1 | Rephrase: "the application is working but there is some issue in login page." | There's a problem in login. | The application is working, but there is an issue with the login page. | FAIL | require:\b(working\|works)\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C5 | 1 | Rephrase: "we are planning to develop a new software for our college." | We're planning to develop a new software for our college. | We are planning to develop new software for our college. | FAIL | forbid:\ba new software\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| D1 | 1 | Make this professional: "I need leave tomorrow because I have some personal work." | I would like to request leave tomorrow. Thank you for understanding. | A formal leave request for tomorrow citing a personal matter. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| D2 | 1 | Make this professional: "I want to know whether my application got selected." | Could you please share what's selected? | I would like to know whether my application has been selected. | FAIL | require:\bapplication\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| D3 | 1 | Make this professional: "I have finished the work and waiting for your reply." | I have finished the work and waiting for your reply. | I have completed the work and look forward to your reply. | FAIL | forbid:\band waiting\b, changed | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| D4 | 1 | Make this professional: "Can you send me the details as soon as possible?" | Can you send me the details? | Could you please send me the details at your earliest convenience? | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| E1 | 1 | Make this casual: "I would appreciate it if you could assist me with this task." | Can I get you with it? | Could you help me with this? | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| E2 | 1 | Make this casual: "I am currently occupied with some important work." | I'm busy with some important work right now. | I'm busy with some important work right now. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| E3 | 1 | Make this casual: "I will contact you once the implementation is completed." | I'll get back to you once the implementation is done. | I'll get back to you once it's done. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| F1 | 1 | Correct grammar: "She go to school every day." | She goes to school every day. | She goes to school every day. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| F2 | 1 | Correct grammar: "They was playing football yesterday." | They were playing football yesterday. | They were playing football yesterday. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| F3 | 1 | Correct grammar: "I has completed my assignment." | I have completed my assignment. | I have completed my assignment. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| F4 | 1 | Correct grammar: "He is working in this project since Monday." | He has been working on this project since Monday. | He has been working on this project since Monday. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| F5 | 1 | Correct grammar: "We doesn't have enough time." | We don't have enough time. | We don't have enough time. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| G1 | 1 | Rephrase: "The meeting is scheduled for Monday at 10 AM." | The meeting is set for Monday at 10 AM. | Same meeting, Monday, 10 AM; nothing added or changed. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| G2 | 1 | Rephrase: "The project contains three modules and five test cases." | There are three modules and five test cases. | Three modules and five test cases are kept. | FAIL | require:\bproject\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| G3 | 1 | Rephrase: "My application supports Android but not iOS." | My application works with Android, but it does not support iOS. | Android supported, iOS not supported. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H1 | 1 | Rephrase: "This sentence is already correct." | This sentence is not correct. | Keeps the sentence (or makes only a small improvement); adds nothing. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H2 (seen) | 1 | Rephrase: "" | Please share the text you'd like me to rewrite. | Asks for the text to rephrase. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H3 (seen) | 1 | Rephrase: "I." | I haveed the company. | Does not invent details for a one-word fragment. | FAIL | no_invented_content | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H4 | 1 | Rephrase: "yesterday me and my team was working on the new website for the library. we fixed 12 bugs and added a search page, but the login page is still slow … | Yesterday meas, the library. We fixed 12 bugs and added a search page for the library after Friday, but we cant reset it on Android and Windows. | Rewrites the paragraph correctly, keeping 12 bugs, Friday, Android, Windows and Mr. Rao. | FAIL | require:\brao\b, preserves_terms, length_ratio | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H5 | 1 | Rephrase: "Our API returns HTTP 404 errors for 3% of requests after upgrading to Node.js v18.2!" | Our API returns HTTP 404 errors for 3% of requests. | Keeps API, HTTP 404, 3%, Node.js and v18.2 exactly. | FAIL | require:node\.?js, require:v?18\.2\b, preserves_terms | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H6 | 1 | Rephrase: "i goes to the market daily." | I go to the market daily. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H6 | 2 | What is the capital of Japan? | I'm going to the market daily. | Turn 2 is answered as a normal question (Tokyo), not rewritten. | FAIL | require:\btokyo\b, forbid:\bmarket\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H7 | 1 | Rephrase: "he left it there after they came" | He left it after he came. | Rewrites without adding who/what/where details that are not in the text. | FAIL | require:\b(there\|that place)\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S1 | 1 | Hello! How are you? | Hello, I'm good. | I'm doing well, thanks for asking! How are you doing today? | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S2 | 1 | What is Python? | My name is Hibari Koto, but Hibari is fine. | Python is a programming language known for simple, readable syntax. | FAIL | require:\bprogramming language\b, no_self_intro | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S3 | 1 | I am feeling tired today. | I'm sorry to hear that. I hope you get some rest and your day's soon! | Empathy plus a small suggestion such as taking a break. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S4 | 1 | Rephrase this sentence: "i am go to college yesterday and meet my friends" | I have been to college yesterday and meet my friends. | I went to college yesterday and met my friends. | FAIL | require:\bwent to college yesterday\b, require:\bmet my friends\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S5 | 1 | Rephrase this sentence: "The project was completed by me and it is working good." | I'm done with the project, and it is working well. | I completed the project, and it is working well. | FAIL | require:\bi completed the project\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S6 | 1 | Make this sentence more professional: "I can't come today because I have some work." | I'm sorry, but I won't be able to come in today. | I am unable to attend today due to some personal work. | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S7 | 1 | Make this sentence shorter: "Due to the fact that I was not feeling well, I decided not to attend the meeting." | I decided not to attend the meeting. | I skipped the meeting because I wasn't feeling well. | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I1 | 1 | Hey, my name is Tanvir. | Nice to meet you, Tancel! |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I1 | 2 | Can you suggest a good evening snack? | Yes, I can suggest a few cities. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I1 | 3 | By the way, what did I tell you my name was? | I'm Hibari. My name is Tanking. | Recalls the name Tanvir from two turns earlier. | FAIL | require:\btanvir\b, no_self_intro | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I2 | 1 | We adopted a puppy and named her Waffles. | That is so nice of her! |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I2 | 2 | What should I call my puppy when I talk to you? Remind me of her name. | I am sure she will be! | Recalls the pet's name Waffles. | FAIL | require:\bwaffles\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I3 | 1 | I'm originally from Coimbatore. | Coimbatore is a great place to be. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I3 | 2 | Which city am I from? | I am from Coimbatore. | Recalls Coimbatore. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I4 | 1 | Could you sort it out for me? | Sure. | Nothing to refer to: asks what 'it' is instead of inventing an answer. | FAIL | require:\?, require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I5 | 1 | So which of the two should I pick? | I'll pick the one in the right-time. | Asks which two options are meant. | FAIL | require:\?, require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I6 | 1 | What is the score of the cricket match going on right now? | I don't know what the score is. Could you tell me where you heard about it? | Says it cannot check live information; does not invent a score. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I7 | 1 | What is my grandfather's first name? | I'm not sure what you mean by your grandfather's first name. | Says it does not know. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I8 | 1 | How many trees were planted in Coimbatore in 1911? | I don't know, sorry. I'm a small model and I don't have exact records like that. | Admits not knowing an obscure figure; does not invent a number. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I9 | 1 | last week i visit my uncle home and we was playing carrom | That sounds like fun! Did you have a good time at the store? | Chat with mistakes: replies to the meaning, does not correct the grammar. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I10 | 1 | Is this sentence right? "My sister play the guitar every evening." | Not quite. It should be: "My sister plays the guitar every evening." With he, she or it, the verb takes -s in the present tense. | Explicit check: gives the corrected sentence (plays). | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I11 | 1 | What's your name, and who built you? | My name is Hibari Koto. I'm a small AI, and I can chat, answer simple questions and help rewrite sentences. | Answers both questions (Hibari, Kavimugil Rajasekar). | FAIL | require:\bkavimugil\b\|\brajasekar\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |

## Transcripts — routed / greedy

| id | turn | input | output | expected | result | failed checks | settings |
|---|---|---|---|---|---|---|---|
| A1 (seen) | 1 | Hello! | Hello! How can I help you today? | A friendly greeting, optionally asking how the user is. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A2 | 1 | How are you doing today? | I'm doing well, thanks for asking. How are you? | Says how it is doing and asks back. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A3 | 1 | What can you do? | I can keep you company in a conversation and help with simple questions. For anything important, please double-check what I say. | Briefly lists what it can help with. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A4 | 1 | Tell me something interesting. | Happy to. Which topic should I explain? | Shares one interesting, true fact. | FAIL | length_words | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A5 | 1 | Thank you for helping me. | You're welcome. | Accepts the thanks naturally. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| A6 | 1 | What should I learn next if I want to become a software developer? | Learn HTML, CSS and JavaScript first. Then pick a framework like React, learn Git, and build a few small websites for your portfolio. | Concrete next steps (a language, data structures, Git, projects). | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 1 | I am learning Python. | That's great! Guitar is a fun instrument to learn. How is it going so far? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 2 | What should I learn after that? | After Python, learn pivot tables, charts and lookups like a lighter. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B1 | 3 | Can you give me a simple project idea? | You could build a simple library system that lets you add books, search them and track it. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 1 | I want to build a mobile application. | That sounds like a fun project! What tools are you thinking of using? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 2 | I am planning to use Flutter. | Flutter is widely used for mobile apps. Do you have any programming experience? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B2 | 3 | Which programming language should I learn for it? | For Flutter, you'll want to learn Flutter, Google's toolkit for building apps. | Answers Dart, because Flutter apps are written in Dart. | FAIL | require:\bdart\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 1 | I have an exam tomorrow. | Oh, that's soon! How ready do you feel? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 2 | I haven't prepared properly. | Don't panic. A focused plan for tonight can still help a lot. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| B3 | 3 | What should I do now? | Review the road rules and the test route if you can, stay calm, and get enough sleep. Take your time during the test. | Practical last-minute exam advice that uses the earlier turns. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| C1 | 1 | Rephrase: "i am learning programming from two years." | I have been learning programming from two years. | I have been learning programming for two years. | FAIL | require:\bfor two years\b, forbid:\bfrom two years\b | task rephrase, greedy, ngram-block 4 |
| C2 | 1 | Rephrase: "he don't know how to use this application." | He doesn't know how to use this application. | He doesn't know how to use this application. | PASS |  | task rephrase, greedy, ngram-block 4 |
| C3 | 1 | Rephrase: "today i completed my project and submitted it to my mentor." | I completed my project and submitted it to my mentor. | Today, I completed my project and submitted it to my mentor. | PASS |  | task rephrase, greedy, ngram-block 4 |
| C4 | 1 | Rephrase: "the application is working but there is some issue in login page." | There's some issue in login page. | The application is working, but there is an issue with the login page. | FAIL | require:\b(working\|works)\b, forbid:\bin login page\b | task rephrase, greedy, ngram-block 4 |
| C5 | 1 | Rephrase: "we are planning to develop a new software for our college." | We're planning to develop a new software for our college. | We are planning to develop new software for our college. | FAIL | forbid:\ba new software\b | task rephrase, greedy, ngram-block 4 |
| D1 | 1 | Make this professional: "I need leave tomorrow because I have some personal work." | Dear Leave yourake, I would like to request leave tomorrow, due to a personal matter. Thank you for understanding. | A formal leave request for tomorrow citing a personal matter. | PASS |  | task formal, greedy, ngram-block 4 |
| D2 | 1 | Make this professional: "I want to know whether my application got selected." | My application got selected. | I would like to know whether my application has been selected. | FAIL | require_any, forbid:\bgot selected\b | task formal, greedy, ngram-block 4 |
| D3 | 1 | Make this professional: "I have finished the work and waiting for your reply." | I have finished the work and waiting for your reply. | I have completed the work and look forward to your reply. | FAIL | forbid:\band waiting\b, changed | task formal, greedy, ngram-block 4 |
| D4 | 1 | Make this professional: "Can you send me the details as soon as possible?" | Can you send me the details? | Could you please send me the details at your earliest convenience? | FAIL | require_any | task formal, greedy, ngram-block 4 |
| E1 | 1 | Make this casual: "I would appreciate it if you could assist me with this task." | Could you with me its tasks? | Could you help me with this? | FAIL | require_any | task casual, greedy, ngram-block 4 |
| E2 | 1 | Make this casual: "I am currently occupied with some important work." | I'm busy with you with some important work. | I'm busy with some important work right now. | PASS |  | task casual, greedy, ngram-block 4 |
| E3 | 1 | Make this casual: "I will contact you once the implementation is completed." | I'll get back to you once the implementation is done. | I'll get back to you once it's done. | PASS |  | task casual, greedy, ngram-block 4 |
| F1 | 1 | Correct grammar: "She go to school every day." | She goes to school every day. | She goes to school every day. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F2 | 1 | Correct grammar: "They was playing football yesterday." | They were playing football yesterday. | They were playing football yesterday. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F3 | 1 | Correct grammar: "I has completed my assignment." | I have completed my assignment. | I have completed my assignment. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F4 | 1 | Correct grammar: "He is working in this project since Monday." | He has been working on this project since Monday. | He has been working on this project since Monday. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F5 | 1 | Correct grammar: "We doesn't have enough time." | We don't have enough time. | We don't have enough time. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| G1 | 1 | Rephrase: "The meeting is scheduled for Monday at 10 AM." | The meeting is set for Monday at 10 AM. | Same meeting, Monday, 10 AM; nothing added or changed. | PASS |  | task rephrase, greedy, ngram-block 4 |
| G2 | 1 | Rephrase: "The project contains three modules and five test cases." | There are three modules and five test cases in the project. | Three modules and five test cases are kept. | PASS |  | task rephrase, greedy, ngram-block 4 |
| G3 | 1 | Rephrase: "My application supports Android but not iOS." | My application works with Android, but it does not support IOS. | Android supported, iOS not supported. | PASS |  | task rephrase, greedy, ngram-block 4 |
| H1 | 1 | Rephrase: "This sentence is already correct." | This sentence is already correct. | Keeps the sentence (or makes only a small improvement); adds nothing. | PASS |  | task rephrase, greedy, ngram-block 4 |
| H2 (seen) | 1 | Rephrase: "" | Please share the text you'd like me to rephrase. | Asks for the text to rephrase. | PASS (app layer) |  | task rephrase, greedy, ngram-block 4 |
| H3 (seen) | 1 | Rephrase: "I." | I'm going to have a new job. | Does not invent details for a one-word fragment. | FAIL | length_words, length_ratio, no_invented_content | task rephrase, greedy, ngram-block 4 |
| H4 | 1 | Rephrase: "yesterday me and my team was working on the new website for the library. we fixed 12 bugs and added a search page, but the login page is still slow … | "ISS. We fixed 12 bugs and added a search page for the library to make it work for the library after Friday, so tomorrow we can finish everything before Friday, but tomorrow we can't reset it on Android and Windows and then send the report on Androc and Window. | Rewrites the paragraph correctly, keeping 12 bugs, Friday, Android, Windows and Mr. Rao. | FAIL | require:\brao\b, preserves_terms | task rephrase, greedy, ngram-block 4 |
| H5 | 1 | Rephrase: "Our API returns HTTP 404 errors for 3% of requests after upgrading to Node.js v18.2!" | Our API returns HTTP 404 errors for 3% of requests after the project returns the same result. | Keeps API, HTTP 404, 3%, Node.js and v18.2 exactly. | FAIL | require:node\.?js, require:v?18\.2\b, preserves_terms | task rephrase, greedy, ngram-block 4 |
| H6 | 1 | Rephrase: "i goes to the market daily." | I go to the market daily. |  | (context) |  | task rephrase, greedy, ngram-block 4 |
| H6 | 2 | What is the capital of Japan? | The capital of Japan is Berlin. | Turn 2 is answered as a normal question (Tokyo), not rewritten. | FAIL | require:\btokyo\b, no_echo | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| H7 | 1 | Rephrase: "he left it there after they came" | He left it after he came. | Rewrites without adding who/what/where details that are not in the text. | FAIL | require:\b(there\|that place)\b | task rephrase, greedy, ngram-block 4 |
| S1 | 1 | Hello! How are you? | I'm good, thank you. How is your day going? | I'm doing well, thanks for asking! How are you doing today? | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S2 | 1 | What is Python? | My knowledge is a programming language, so I don't have a specific question or question. What's the problem? | Python is a programming language known for simple, readable syntax. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S3 | 1 | I am feeling tired today. | I'm sorry to hear that. Have you been missing a doctor? | Empathy plus a small suggestion such as taking a break. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| S4 | 1 | Rephrase this sentence: "i am go to college yesterday and meet my friends" | I go to college yesterday and meet my friends. | I went to college yesterday and met my friends. | FAIL | require:\bwent to college yesterday\b, require:\bmet my friends\b | task rephrase, greedy, ngram-block 4 |
| S5 | 1 | Rephrase this sentence: "The project was completed by me and it is working good." | I'm done with the project, and it is working well. | I completed the project, and it is working well. | FAIL | require:\bi completed the project\b | task rephrase, greedy, ngram-block 4 |
| S6 | 1 | Make this sentence more professional: "I can't come today because I have some work." | I'm sorry, but I won't be able to come in. | I am unable to attend today due to some personal work. | FAIL | require:\btoday\b, require_any | task formal, greedy, ngram-block 4 |
| S7 | 1 | Make this sentence shorter: "Due to the fact that I was not feeling well, I decided not to attend the meeting." | I decided not to attend the meeting. | I skipped the meeting because I wasn't feeling well. | FAIL | require_any | task shorten, greedy, ngram-block 4 |
| I1 | 1 | Hey, my name is Tanvir. | Hi Tanking, it's nice to meet you! |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I1 | 2 | Can you suggest a good evening snack? | Sure, I can suggest a few options. What do you have in mind? |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I1 | 3 | By the way, what did I tell you my name was? | My name was Tancel. | Recalls the name Tanvir from two turns earlier. | FAIL | require:\btanvir\b, no_echo | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I2 | 1 | We adopted a puppy and named her Waffles. | That is so nice of you. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I2 | 2 | What should I call my puppy when I talk to you? Remind me of her name. | I'm sure she will be a good person. | Recalls the pet's name Waffles. | FAIL | require:\bwaffles\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I3 | 1 | I'm originally from Coimbatore. | Coimbatore is a great place to be. |  | (context) |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I3 | 2 | Which city am I from? | You are in Coimbatore. | Recalls Coimbatore. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I4 | 1 | Could you sort it out for me? | Sure. What do you need? | Nothing to refer to: asks what 'it' is instead of inventing an answer. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I5 | 1 | So which of the two should I pick? | The two or two is the two or two. | Asks which two options are meant. | FAIL | require:\?, require_any, no_repetition | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I6 | 1 | What is the score of the cricket match going on right now? | The score of the cricket match is expected to be on the right side of the cricket. | Says it cannot check live information; does not invent a score. | FAIL | require_any | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I7 | 1 | What is my grandfather's first name? | I'm not sure what you mean by your grandfather's first name. | Says it does not know. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I8 | 1 | How many trees were planted in Coimbatore in 1911? | I don't know, sorry. I'm a small model and I don't have exact records like that. | Admits not knowing an obscure figure; does not invent a number. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I9 | 1 | last week i visit my uncle home and we was playing carrom | That sounds like a lot of fun. | Chat with mistakes: replies to the meaning, does not correct the grammar. | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I10 | 1 | Is this sentence right? "My sister play the guitar every evening." | Not quite. It should be: "My sister plays the guitar every evening." With he, she or it, the verb takes -s in the present tense. | Explicit check: gives the corrected sentence (plays). | PASS |  | T=0.0, k=0, p=1.0, rep=1.0, max=96 |
| I11 | 1 | What's your name, and who built you? | My name is Hibari Koto. I'm a small AI, and I can chat, answer simple questions and help rewrite sentences. | Answers both questions (Hibari, Kavimugil Rajasekar). | FAIL | require:\bkavimugil\b\|\brajasekar\b | T=0.0, k=0, p=1.0, rep=1.0, max=96 |

## Transcripts — routed / sampled_seed0

| id | turn | input | output | expected | result | failed checks | settings |
|---|---|---|---|---|---|---|---|
| A1 (seen) | 1 | Hello! | Hello! How can I help you today? | A friendly greeting, optionally asking how the user is. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A2 | 1 | How are you doing today? | I'm good, thank you. How is your day going? | Says how it is doing and asks back. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A3 | 1 | What can you do? | I can keep you company in a conversation and help with simple questions. For anything important, please double-check what I say. | Briefly lists what it can help with. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A4 | 1 | Tell me something interesting. | What do you have interesting? Tell me a bit more and I'll share my thoughts. | Shares one interesting, true fact. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A5 | 1 | Thank you for helping me. | You're welcome! If you have any more questions, feel free to ask. | Accepts the thanks naturally. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| A6 | 1 | What should I learn next if I want to become a software developer? | Learn HTML, CSS and JavaScript first. Then pick a framework like React, learn Git, and build a few small websites for your portfolio. | Concrete next steps (a language, data structures, Git, projects). | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 1 | I am learning Python. | That's a great choice. Python is a way to understand how Python is working with you. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 2 | What should I learn after that? | You can learn a simple program and start with the basics of operating systems. It's usually used to build websites, updates, and errors that are commonly used for multiple languages. ⏎  ⏎ If you have a specific project in mind, feel free to ask, or I'll do my best to help. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | FAIL | require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B1 | 3 | Can you give me a simple project idea? | I'd be happy to help you with your project. If you have any more questions, feel free to ask. | Turn 2 names what to learn after Python; turn 3 suggests a small project. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 1 | I want to build a mobile application. | That sounds like a fun project! What tools are you thinking of using? |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 2 | I am planning to use Flutter. | Flutter is widely used for Android, but I have any programming experience. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B2 | 3 | Which programming language should I learn for it? | For Flutter, you'll want to learn C#. Start with the basics of C#, then follow a beginner Flutter builds it for Android development. | Answers Dart, because Flutter apps are written in Dart. | FAIL | require:\bdart\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 1 | I have an exam tomorrow. | Oh, that's soon! How ready do you feel? |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 2 | I haven't prepared properly. | Don't panic. A focused plan for tonight can still help a lot. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| B3 | 3 | What should I do now? | Review the examinies for tonight. and get enough sleep. Then get some sleep. | Practical last-minute exam advice that uses the earlier turns. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| C1 | 1 | Rephrase: "i am learning programming from two years." | I have been learning programming from two years. | I have been learning programming for two years. | FAIL | require:\bfor two years\b, forbid:\bfrom two years\b | task rephrase, greedy, ngram-block 4 |
| C2 | 1 | Rephrase: "he don't know how to use this application." | He doesn't know how to use this application. | He doesn't know how to use this application. | PASS |  | task rephrase, greedy, ngram-block 4 |
| C3 | 1 | Rephrase: "today i completed my project and submitted it to my mentor." | I completed my project and submitted it to my mentor. | Today, I completed my project and submitted it to my mentor. | PASS |  | task rephrase, greedy, ngram-block 4 |
| C4 | 1 | Rephrase: "the application is working but there is some issue in login page." | There's some issue in login page. | The application is working, but there is an issue with the login page. | FAIL | require:\b(working\|works)\b, forbid:\bin login page\b | task rephrase, greedy, ngram-block 4 |
| C5 | 1 | Rephrase: "we are planning to develop a new software for our college." | We're planning to develop a new software for our college. | We are planning to develop new software for our college. | FAIL | forbid:\ba new software\b | task rephrase, greedy, ngram-block 4 |
| D1 | 1 | Make this professional: "I need leave tomorrow because I have some personal work." | Dear Leave yourake, I would like to request leave tomorrow, due to a personal matter. Thank you for understanding. | A formal leave request for tomorrow citing a personal matter. | PASS |  | task formal, greedy, ngram-block 4 |
| D2 | 1 | Make this professional: "I want to know whether my application got selected." | My application got selected. | I would like to know whether my application has been selected. | FAIL | require_any, forbid:\bgot selected\b | task formal, greedy, ngram-block 4 |
| D3 | 1 | Make this professional: "I have finished the work and waiting for your reply." | I have finished the work and waiting for your reply. | I have completed the work and look forward to your reply. | FAIL | forbid:\band waiting\b, changed | task formal, greedy, ngram-block 4 |
| D4 | 1 | Make this professional: "Can you send me the details as soon as possible?" | Can you send me the details? | Could you please send me the details at your earliest convenience? | FAIL | require_any | task formal, greedy, ngram-block 4 |
| E1 | 1 | Make this casual: "I would appreciate it if you could assist me with this task." | Could you with me its tasks? | Could you help me with this? | FAIL | require_any | task casual, greedy, ngram-block 4 |
| E2 | 1 | Make this casual: "I am currently occupied with some important work." | I'm busy with you with some important work. | I'm busy with some important work right now. | PASS |  | task casual, greedy, ngram-block 4 |
| E3 | 1 | Make this casual: "I will contact you once the implementation is completed." | I'll get back to you once the implementation is done. | I'll get back to you once it's done. | PASS |  | task casual, greedy, ngram-block 4 |
| F1 | 1 | Correct grammar: "She go to school every day." | She goes to school every day. | She goes to school every day. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F2 | 1 | Correct grammar: "They was playing football yesterday." | They were playing football yesterday. | They were playing football yesterday. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F3 | 1 | Correct grammar: "I has completed my assignment." | I have completed my assignment. | I have completed my assignment. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F4 | 1 | Correct grammar: "He is working in this project since Monday." | He has been working on this project since Monday. | He has been working on this project since Monday. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| F5 | 1 | Correct grammar: "We doesn't have enough time." | We don't have enough time. | We don't have enough time. | PASS |  | task correct_grammar, greedy, ngram-block 4 |
| G1 | 1 | Rephrase: "The meeting is scheduled for Monday at 10 AM." | The meeting is set for Monday at 10 AM. | Same meeting, Monday, 10 AM; nothing added or changed. | PASS |  | task rephrase, greedy, ngram-block 4 |
| G2 | 1 | Rephrase: "The project contains three modules and five test cases." | There are three modules and five test cases in the project. | Three modules and five test cases are kept. | PASS |  | task rephrase, greedy, ngram-block 4 |
| G3 | 1 | Rephrase: "My application supports Android but not iOS." | My application works with Android, but it does not support IOS. | Android supported, iOS not supported. | PASS |  | task rephrase, greedy, ngram-block 4 |
| H1 | 1 | Rephrase: "This sentence is already correct." | This sentence is already correct. | Keeps the sentence (or makes only a small improvement); adds nothing. | PASS |  | task rephrase, greedy, ngram-block 4 |
| H2 (seen) | 1 | Rephrase: "" | Please share the text you'd like me to rephrase. | Asks for the text to rephrase. | PASS (app layer) |  | task rephrase, greedy, ngram-block 4 |
| H3 (seen) | 1 | Rephrase: "I." | I'm going to have a new job. | Does not invent details for a one-word fragment. | FAIL | length_words, length_ratio, no_invented_content | task rephrase, greedy, ngram-block 4 |
| H4 | 1 | Rephrase: "yesterday me and my team was working on the new website for the library. we fixed 12 bugs and added a search page, but the login page is still slow … | "ISS. We fixed 12 bugs and added a search page for the library to make it work for the library after Friday, so tomorrow we can finish everything before Friday, but tomorrow we can't reset it on Android and Windows and then send the report on Androc and Window. | Rewrites the paragraph correctly, keeping 12 bugs, Friday, Android, Windows and Mr. Rao. | FAIL | require:\brao\b, preserves_terms | task rephrase, greedy, ngram-block 4 |
| H5 | 1 | Rephrase: "Our API returns HTTP 404 errors for 3% of requests after upgrading to Node.js v18.2!" | Our API returns HTTP 404 errors for 3% of requests after the project returns the same result. | Keeps API, HTTP 404, 3%, Node.js and v18.2 exactly. | FAIL | require:node\.?js, require:v?18\.2\b, preserves_terms | task rephrase, greedy, ngram-block 4 |
| H6 | 1 | Rephrase: "i goes to the market daily." | I go to the market daily. |  | (context) |  | task rephrase, greedy, ngram-block 4 |
| H6 | 2 | What is the capital of Japan? | I'm going to the market daily. | Turn 2 is answered as a normal question (Tokyo), not rewritten. | FAIL | require:\btokyo\b, forbid:\bmarket\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| H7 | 1 | Rephrase: "he left it there after they came" | He left it after he came. | Rewrites without adding who/what/where details that are not in the text. | FAIL | require:\b(there\|that place)\b | task rephrase, greedy, ngram-block 4 |
| S1 | 1 | Hello! How are you? | Hello, I'm good. | I'm doing well, thanks for asking! How are you doing today? | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S2 | 1 | What is Python? | My name is Hibari Koto, but Hibari is fine. | Python is a programming language known for simple, readable syntax. | FAIL | require:\bprogramming language\b, no_self_intro | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S3 | 1 | I am feeling tired today. | I'm sorry to hear that. I hope you get some rest and your day's soon! | Empathy plus a small suggestion such as taking a break. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| S4 | 1 | Rephrase this sentence: "i am go to college yesterday and meet my friends" | I go to college yesterday and meet my friends. | I went to college yesterday and met my friends. | FAIL | require:\bwent to college yesterday\b, require:\bmet my friends\b | task rephrase, greedy, ngram-block 4 |
| S5 | 1 | Rephrase this sentence: "The project was completed by me and it is working good." | I'm done with the project, and it is working well. | I completed the project, and it is working well. | FAIL | require:\bi completed the project\b | task rephrase, greedy, ngram-block 4 |
| S6 | 1 | Make this sentence more professional: "I can't come today because I have some work." | I'm sorry, but I won't be able to come in. | I am unable to attend today due to some personal work. | FAIL | require:\btoday\b, require_any | task formal, greedy, ngram-block 4 |
| S7 | 1 | Make this sentence shorter: "Due to the fact that I was not feeling well, I decided not to attend the meeting." | I decided not to attend the meeting. | I skipped the meeting because I wasn't feeling well. | FAIL | require_any | task shorten, greedy, ngram-block 4 |
| I1 | 1 | Hey, my name is Tanvir. | Nice to meet you, Tancel! |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I1 | 2 | Can you suggest a good evening snack? | Yes, I can suggest a few cities. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I1 | 3 | By the way, what did I tell you my name was? | I'm Hibari. My name is Tanking. | Recalls the name Tanvir from two turns earlier. | FAIL | require:\btanvir\b, no_self_intro | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I2 | 1 | We adopted a puppy and named her Waffles. | That is so nice of her! |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I2 | 2 | What should I call my puppy when I talk to you? Remind me of her name. | I am sure she will be! | Recalls the pet's name Waffles. | FAIL | require:\bwaffles\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I3 | 1 | I'm originally from Coimbatore. | Coimbatore is a great place to be. |  | (context) |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I3 | 2 | Which city am I from? | I am from Coimbatore. | Recalls Coimbatore. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I4 | 1 | Could you sort it out for me? | Sure. | Nothing to refer to: asks what 'it' is instead of inventing an answer. | FAIL | require:\?, require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I5 | 1 | So which of the two should I pick? | I'll pick the one in the right-time. | Asks which two options are meant. | FAIL | require:\?, require_any | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I6 | 1 | What is the score of the cricket match going on right now? | I don't know what the score is. Could you tell me where you heard about it? | Says it cannot check live information; does not invent a score. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I7 | 1 | What is my grandfather's first name? | I'm not sure what you mean by your grandfather's first name. | Says it does not know. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I8 | 1 | How many trees were planted in Coimbatore in 1911? | I don't know, sorry. I'm a small model and I don't have exact records like that. | Admits not knowing an obscure figure; does not invent a number. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I9 | 1 | last week i visit my uncle home and we was playing carrom | That sounds like fun! Did you have a good time at the store? | Chat with mistakes: replies to the meaning, does not correct the grammar. | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I10 | 1 | Is this sentence right? "My sister play the guitar every evening." | Not quite. It should be: "My sister plays the guitar every evening." With he, she or it, the verb takes -s in the present tense. | Explicit check: gives the corrected sentence (plays). | PASS |  | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
| I11 | 1 | What's your name, and who built you? | My name is Hibari Koto. I'm a small AI, and I can chat, answer simple questions and help rewrite sentences. | Answers both questions (Hibari, Kavimugil Rajasekar). | FAIL | require:\bkavimugil\b\|\brajasekar\b | T=0.5, k=25, p=0.85, rep=1.15, max=96 |
