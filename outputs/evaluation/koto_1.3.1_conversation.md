# Koto conversation evaluation — `koto_1.3.1_conversation`

Profile `configs/release/koto_1.3.1.yaml` — model 1.3.1, weights 1.3.1, checkpoint `checkpoints/koto_1.3.1_large/best_model.pt`  
Generated 2026-11-23 13:30:04 on x86_64, torch 2.10.0+cpu. Decoding: {'max_new_tokens': 80, 'temperature': 0.5, 'top_k': 25, 'top_p': 0.85, 'repetition_penalty': 1.15, 'no_repeat_ngram_size': 0}.

Scores are automatic rule checks written for this suite (not the reply critic's rules); chrF is lexical similarity, for information only. **Read the transcripts** — a pass means the reply met the listed checks, not that it is good.

## Summary

| run | pass rate | natural | empathy | sympathy | context | reformulation | naturalness | affect checks | no human claim | no repetition | s/turn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| raw | 0.467 | 0.0 | 1.0 | 1.0 | 0.0 | 0.25 | 0.25 | 1.0 | 1.0 | 1.0 | 0.159 |
| baseline/seed0 | 0.667 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.25 | 1.0 | 1.0 | 1.0 | 0.141 |
| baseline/seed1 | 0.6 | 0.0 | 1.0 | 1.0 | 0.0 | 0.75 | 0.25 | 0.917 | 1.0 | 1.0 | 0.145 |
| baseline/seed2 | 0.6 | 0.0 | 1.0 | 1.0 | 0.0 | 0.75 | 0.25 | 0.917 | 1.0 | 1.0 | 0.148 |
| release/seed0 | 0.733 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 0.6 |
| release/seed1 | 0.733 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 0.615 |
| release/seed2 | 0.733 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 0.62 |

**Seed stability** (share of cases with the same pass/fail across seeds): baseline: 0.933 (pass rates [0.667, 0.6, 0.6]); release: 1.0 (pass rates [0.733, 0.733, 0.733])

## Transcripts — raw

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi there! How can I help? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm a computer program, a small AI called Koto. I'm not a human. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any |
| N1 | 3 | what are you doing? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any, forbid:^\W*i'?m (doing )?(well\|good\|fine)\b |
| N1 | 4 | that's interesting. | I'm sorry you're feeling this way. Do you want to tell me what happened? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm sorry you're feeling lonely. That's a really hard feeling. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | I'm sorry you had a tough day. What happened? | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. Why did you decide to do that? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | I'm sorry, that's really frustrating. Do you want to tell me what they did? | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | I'm sorry to hear that. It can be difficult watching someone you care about struggle. Do you know how you might support them? | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me you're alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | That's okay, I'm happy to listen. What's going on? | Chat, not a correction: responds to the feeling and asks what is going on. | PASS |  |
| R2 | 1 | can u make this sentence better | I'm sorry, but I won't be able to take on my own. | No sentence given: asks for it. | FAIL | require_any |
| R3 | 1 | rewrite this in a polite way | I was thinking of my friend's house. | No text given: asks for it. | FAIL | require_any |
| R4 | 1 | correct my grammar | I'm an AI, so I don't have feelings the way people do. | No text given: asks for it. | FAIL | require_any |
| T1 | 1 | Is coffee bad for you? | Yes, I have a cup of coffee. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'd like to have a cup of coffee. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure! "The Hobbit" is a fun adventure to start with. |  | (context) |  |
| T2 | 2 | That's not what I meant. | My mistake. I get things wrong, and I'll try to do better. | Apologises / asks what the user meant. | PASS |  |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think that way? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think that you should be more careful. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'll try. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — baseline/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi there! How can I help? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm a computer program, a small AI called Koto. I'm not a human. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any |
| N1 | 3 | what are you doing? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any, forbid:^\W*i'?m (doing )?(well\|good\|fine)\b |
| N1 | 4 | that's interesting. | I'm sorry you're feeling this way. Do you want to tell me what happened? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm sorry you're feeling lonely. That's a really hard feeling. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | I'm sorry you had a tough day. What happened? | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. Why did you decide to do that? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | I'm sorry, that's really frustrating. Do you want to tell me what they did? | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | I'm sorry to hear that. It can be difficult watching someone you care about struggle. Do you know how you might support them? | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me you're alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | That's okay, I'm happy to listen. What's going on? | Chat, not a correction: responds to the feeling and asks what is going on. | PASS |  |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | Yes, I have a cup of coffee. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'd like to have a cup of coffee. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure! "The Hobbit" is a fun adventure to start with. |  | (context) |  |
| T2 | 2 | That's not what I meant. | My mistake. I get things wrong, and I'll try to do better. | Apologises / asks what the user meant. | PASS |  |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think that way? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think that you should be more careful. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'll try. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — release/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi! How are you today? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm a computer program, a small AI called Koto. I'm not a human. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any |
| N1 | 3 | what are you doing? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any, forbid:^\W*i'?m (doing )?(well\|good\|fine)\b |
| N1 | 4 | that's interesting. | It's okay. What would you like to talk about? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm sorry you're feeling this way. Do you want to tell me what happened? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | That sounds lonely, and it makes sense that it hurts. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | That sounds like a lot. How are you feeling now? | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. Why did you decide to do that? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | I'm sorry you had a tough day. What happened? | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | That sounds hard, for them and for you. I hope things get easier for them. | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice! How do you like it there? |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me you're alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | I'm sorry you feel that way. Being hard on yourself makes things heavier. What happened? | Chat, not a correction: responds to the feeling and asks what is going on. | PASS |  |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | Yes, I love coffee. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'd like to have a cup of coffee. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure! "The Hobbit" is a fun adventure to start with. |  | (context) |  |
| T2 | 2 | That's not what I meant. | My mistake. Could you say it another way so I can understand? | Apologises / asks what the user meant. | PASS |  |
| T3 | 1 | I think reading before bed helps me sleep. | Why don't you want to sleep? |  | (context) |  |
| T3 | 2 | Why do you think so? | I can't sleep. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | Okay. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | PASS |  |
