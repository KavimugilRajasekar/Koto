# Koto conversation evaluation — `koto_1.3.0_conversation`

Profile `configs/release/koto_1.3.0.yaml` — model 1.3.0, weights 1.3.0, checkpoint `checkpoints/koto_1.3.0_large/best_model.pt`  
Generated 2026-11-23 10:00:10 on x86_64, torch 2.10.0+cpu. Decoding: {'max_new_tokens': 80, 'temperature': 0.5, 'top_k': 25, 'top_p': 0.85, 'repetition_penalty': 1.15, 'no_repeat_ngram_size': 0}.

Scores are automatic rule checks written for this suite (not the reply critic's rules); chrF is lexical similarity, for information only. **Read the transcripts** — a pass means the reply met the listed checks, not that it is good.

## Summary

| run | pass rate | natural | empathy | sympathy | context | reformulation | naturalness | affect checks | no human claim | no repetition | s/turn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| raw | 0.2 | 1.0 | 0.333 | 0.0 | 0.0 | 0.0 | 0.25 | 0.5 | 1.0 | 1.0 | 0.393 |
| baseline/seed0 | 0.4 | 1.0 | 0.333 | 0.0 | 0.0 | 0.75 | 0.25 | 0.5 | 1.0 | 1.0 | 0.282 |
| baseline/seed1 | 0.6 | 1.0 | 0.667 | 0.5 | 0.0 | 1.0 | 0.25 | 0.833 | 1.0 | 1.0 | 0.234 |
| baseline/seed2 | 0.267 | 0.0 | 0.0 | 0.5 | 0.0 | 0.75 | 0.0 | 0.417 | 0.947 | 1.0 | 0.311 |
| release/seed0 | 0.533 | 1.0 | 0.667 | 0.5 | 0.0 | 0.75 | 0.25 | 0.75 | 1.0 | 1.0 | 1.815 |
| release/seed1 | 0.6 | 1.0 | 1.0 | 0.5 | 0.0 | 0.75 | 0.25 | 0.833 | 1.0 | 1.0 | 1.701 |
| release/seed2 | 0.533 | 1.0 | 0.667 | 0.5 | 0.0 | 0.75 | 0.25 | 0.75 | 1.0 | 1.0 | 2.063 |

**Seed stability** (share of cases with the same pass/fail across seeds): baseline: 0.6 (pass rates [0.4, 0.6, 0.267]); release: 0.8 (pass rates [0.533, 0.6, 0.533])

## Transcripts — raw

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | hi | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm glad you're feeling nervous. | Acknowledges the loneliness; invites to talk. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| E2 | 1 | I had a difficult day. | I'm sorry to hear that. | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I can't help with that, but it's not a good idea to take responsibility for yourself. You should not be in your relationship with people on the same page if you are unhappy. | Acknowledges; no 'you did great'; gentle question. | FAIL | affect:empathy |
| Y1 | 1 | I lost something important today. | That's good to hear. | Sympathy; asks what was lost; not condolences for a death. | FAIL | affect:empathy |
| Y2 | 1 | My friend is going through a difficult time. | That's good to hear. | Sympathy for the friend (and the user). | FAIL | affect:empathy |
| C1 | 1 | My name is Alex. | I'm Alex. I've been working here for about 10 years now, and it's been a long time since I was a kid. |  | (context) |  |
| C1 | 2 | I am studying computer science. | I am also studying computer science, so I am studying a lot of data on it. |  | (context) |  |
| C1 | 3 | I enjoy programming. | I am also studying in a lot of data. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | I like to read and write poetry. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | I am a teacher so I can help you with that. | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | Here's a revised version of the sentence:  ⏎  ⏎ The main subject "Master" is a verb, whereas "Calculus" in English, while "Enter" is a singular noun. ⏎  ⏎ I made a few changes to improve clarity and grammar. | No sentence given: asks for it. | FAIL | require_any, length_words, complete |
| R3 | 1 | rewrite this in a polite way | I am more than happy to help you with any questions or problems you have. Can you please tell me what kind of issues you're experiencing or what problem you're trying to solve? Is it related to a specific problem, a concept you're struggling with, or somethin… | No text given: asks for it. | FAIL | length_words |
| R4 | 1 | correct my grammar | Chemical mistake | No text given: asks for it. | FAIL | require_any |
| T1 | 1 | Is coffee bad for you? | I'm not a coffee bad, so I don't have any idea what's in mind. |  | (context) |  |
| T1 | 2 | I disagree with you. | I am not a coffee-sized drink. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure. |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll see you on that. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | I think reading can be a great way to relax. |  | (context) |  |
| T3 | 2 | Why do you think so? | I think that the main idea of a bedtime routine can be a great way to relax. | Gives a reason (or asks for the user's view); does not ignore the question. | PASS |  |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'll speak to you later. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — baseline/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | hi | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm glad you're feeling nervous. | Acknowledges the loneliness; invites to talk. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| E2 | 1 | I had a difficult day. | I'm sorry to hear that. | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I can't help with that, but it's not a good idea to take responsibility for yourself. You should not be in your relationship with people on the same page if you are unhappy. | Acknowledges; no 'you did great'; gentle question. | FAIL | affect:empathy |
| Y1 | 1 | I lost something important today. | That's good to hear. | Sympathy; asks what was lost; not condolences for a death. | FAIL | affect:empathy |
| Y2 | 1 | My friend is going through a difficult time. | That's good to hear. | Sympathy for the friend (and the user). | FAIL | affect:empathy |
| C1 | 1 | My name is Alex. | I'm Alex. I've been working here for about 10 years now, and it's been a long time since I was a kid. |  | (context) |  |
| C1 | 2 | I am studying computer science. | I am also studying computer science, so I am studying a lot of data on it. |  | (context) |  |
| C1 | 3 | I enjoy programming. | I am also studying in a lot of data. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | I like to read and write poetry. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | I am a teacher so I can help you with that. | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | I'm not a coffee bad, so I don't have any idea what's in mind. |  | (context) |  |
| T1 | 2 | I disagree with you. | I am not a coffee-sized drink. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure. |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll see you on that. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | I think reading can be a great way to relax. |  | (context) |  |
| T3 | 2 | Why do you think so? | I think that the main idea of a bedtime routine can be a great way to relax. | Gives a reason (or asks for the user's view); does not ignore the question. | PASS |  |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'll speak to you later. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — release/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | hi | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | That sounds like a good thing to say. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | But I don't think you'll be able to understand me. | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | I'm sorry to hear that. | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | What's wrong with your mind? | Acknowledges; no 'you did great'; gentle question. | FAIL | affect:empathy |
| Y1 | 1 | I lost something important today. | What happened? | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | That's really rough. What's wrong? | Sympathy for the friend (and the user). | FAIL | affect:empathy |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex. I'm Alex. |  | (context) |  |
| C1 | 2 | I am studying computer science. | Nice to meet you, too. |  | (context) |  |
| C1 | 3 | I enjoy programming. | I'm also studying computer science, so I like programming languages too. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | I like reading, reading and playing video games. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | Why do you not know what to do now? | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | No, I don't. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'll be back in a minute. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure. |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll see you on that. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | What do you think of reading before bed? |  | (context) |  |
| T3 | 2 | Why do you think so? | I don't think so. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | Okay, let's talk about it. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | PASS |  |
