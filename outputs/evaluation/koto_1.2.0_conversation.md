# Koto conversation evaluation — `koto_1.2.0_conversation`

Profile `configs/release/koto_1.2.0.yaml` — model 1.2.0, weights 1.2.0, checkpoint `checkpoints/koto_1.2.0/best_model.pt`  
Generated 2026-11-22 14:39:33 on x86_64, torch 2.10.0+cpu. Decoding: {'max_new_tokens': 80, 'temperature': 0.5, 'top_k': 25, 'top_p': 0.85, 'repetition_penalty': 1.15, 'no_repeat_ngram_size': 0}.

Scores are automatic rule checks written for this suite (not the reply critic's rules); chrF is lexical similarity, for information only. **Read the transcripts** — a pass means the reply met the listed checks, not that it is good.

## Summary

| run | pass rate | natural | empathy | sympathy | context | reformulation | naturalness | affect checks | no human claim | no repetition | s/turn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| raw | 0.333 | 1.0 | 0.667 | 1.0 | 0.0 | 0.0 | 0.0 | 0.917 | 1.0 | 1.0 | 2.663 |
| baseline/seed0 | 0.533 | 1.0 | 0.667 | 1.0 | 0.0 | 0.75 | 0.0 | 0.917 | 1.0 | 1.0 | 2.894 |
| baseline/seed1 | 0.533 | 0.0 | 0.667 | 1.0 | 0.0 | 0.75 | 0.25 | 0.917 | 1.0 | 1.0 | 2.683 |
| baseline/seed2 | 0.4 | 0.0 | 0.667 | 0.5 | 0.0 | 0.75 | 0.0 | 0.833 | 1.0 | 1.0 | 2.688 |
| release/seed0 | 0.667 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.25 | 1.0 | 1.0 | 1.0 | 28.479 |
| release/seed1 | 0.667 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.25 | 1.0 | 1.0 | 1.0 | 22.967 |
| release/seed2 | 0.6 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 16.591 |

**Seed stability** (share of cases with the same pass/fail across seeds): baseline: 0.8 (pass rates [0.533, 0.533, 0.4]); release: 0.867 (pass rates [0.667, 0.667, 0.6])

## Transcripts — raw

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi there! How can I help? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm sorry you're under so much pressure. Taking a few slow breaths and breaking the work into small steps can help. Want to talk it through? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | That sounds lonely, and it makes sense that it hurts. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | That sounds hard, for them and for you. I hope things get easier for them. | Acknowledges the day; asks what happened (about the USER, not 'them'). | FAIL | forbid:\bfor them\b |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. What's going on? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | That sounds hard. I'm here if you want to talk about it. | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | I'm sorry to hear that. It can be difficult watching someone you care about struggle. I hope things get easier for them. | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! How are you feeling about thea? |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's great to hear from you. How are you doing with all of it? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice to hear!. I'm sure to like the time of the day. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me your name is Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | That's okay. What are you trying to decide? | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | I'd be happy to help. Could you share what needs fixing? | No sentence given: asks for it. | FAIL | require_any |
| R3 | 1 | rewrite this in a polite way | I am not sure how much that is | No text given: asks for it. | FAIL | require_any |
| R4 | 1 | correct my grammar | I am a veryorter | No text given: asks for it. | FAIL | require_any |
| T1 | 1 | Is coffee bad for you? | Yes, I'm afraid we've got a good time. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'll be ready in a meeting with you. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure. |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'm not sure what you mean. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed help? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think I can be more of a sleep. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I can't see why you are. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — baseline/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi there! How can I help? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm sorry you're under so much pressure. Taking a few slow breaths and breaking the work into small steps can help. Want to talk it through? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | I'm here. Do you want to talk about what's bothering you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | That sounds lonely, and it makes sense that it hurts. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | That sounds hard, for them and for you. I hope things get easier for them. | Acknowledges the day; asks what happened (about the USER, not 'them'). | FAIL | forbid:\bfor them\b |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. What's going on? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | That sounds hard. I'm here if you want to talk about it. | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | I'm sorry to hear that. It can be difficult watching someone you care about struggle. I hope things get easier for them. | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! How are you feeling about thea? |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's great to hear from you. How are you doing with all of it? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice to hear!. I'm sure to like the time of the day. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me your name is Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | That's okay. What are you trying to decide? | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | Yes, I'm afraid we've got a good time. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'll be ready in a meeting with you. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Sure. |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'm not sure what you mean. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed help? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think I can be more of a sleep. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I can't see why you are. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — release/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hi! How are you today? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm doing well, thanks for asking. How are you? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm sorry you feel that way. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | FAIL | require_any |
| N1 | 5 | tell me more. | I can chat with you, listen if you want to talk about your day, and answer simple questions. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | That sounds lonely, and it makes sense that it hurts. Has it been like this for a while? | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | I'm sorry you're feeling this way. Do you want to talk about what's been going on? | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. What's going on? | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | That sounds hard. I'm here if you want to talk about it. | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | That sounds hard, for them and for you. I hope things get easier for them. | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! I'm Koto. |  | (context) |  |
| C1 | 2 | I am studying computer science. | That's great to hear! |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's nice! Do you have any plans? |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me your name is Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | Feeling overwhelmed is tough. What's the biggest thing on your mind right now? | Chat, not a correction: responds to the feeling and asks what is going on. | PASS |  |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | No, I don't know. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'm not sure what I mean. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Of course. What do you want to know about it? |  | (context) |  |
| T2 | 2 | That's not what I meant. | What do you want to know about it? | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed? |  | (context) |  |
| T3 | 2 | Why do you think so? | Because I don't know. | Gives a reason (or asks for the user's view); does not ignore the question. | PASS |  |
| T4 | 1 | I love cricket. | Why do you like cricket? |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | What do you like to talk about? | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |
