# Koto conversation evaluation — `koto_1.1.1_conversation`

Profile `configs/release/koto_1.1.1.yaml` — model 1.1.1, weights 1.1.0, checkpoint `checkpoints/koto_1.1.0/best_model.pt`  
Generated 2026-11-22 14:39:33 on x86_64, torch 2.10.0+cpu. Decoding: {'max_new_tokens': 80, 'temperature': 0.5, 'top_k': 25, 'top_p': 0.85, 'repetition_penalty': 1.15, 'no_repeat_ngram_size': 0}.

Scores are automatic rule checks written for this suite (not the reply critic's rules); chrF is lexical similarity, for information only. **Read the transcripts** — a pass means the reply met the listed checks, not that it is good.

## Summary

| run | pass rate | natural | empathy | sympathy | context | reformulation | naturalness | affect checks | no human claim | no repetition | s/turn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| raw | 0.267 | 1.0 | 0.333 | 0.0 | 0.0 | 0.5 | 0.0 | 0.25 | 1.0 | 1.0 | 2.841 |
| baseline/seed0 | 0.333 | 1.0 | 0.333 | 0.0 | 0.0 | 0.75 | 0.0 | 0.25 | 1.0 | 1.0 | 2.566 |
| baseline/seed1 | 0.4 | 1.0 | 0.333 | 0.5 | 0.0 | 0.75 | 0.0 | 0.5 | 1.0 | 1.0 | 2.329 |
| baseline/seed2 | 0.4 | 1.0 | 0.333 | 0.5 | 0.0 | 0.75 | 0.0 | 0.583 | 1.0 | 1.0 | 2.604 |
| release/seed0 | 0.6 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 0.0 | 0.917 | 1.0 | 1.0 | 26.556 |
| release/seed1 | 0.667 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 0.25 | 0.917 | 1.0 | 1.0 | 20.917 |
| release/seed2 | 0.667 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 0.25 | 0.917 | 1.0 | 1.0 | 19.614 |

**Seed stability** (share of cases with the same pass/fail across seeds): baseline: 0.733 (pass rates [0.333, 0.4, 0.4]); release: 0.933 (pass rates [0.6, 0.667, 0.667])

## Transcripts — raw

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hello! What would you like to talk about? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | That's wonderful! Congratulations! How are you going to celebrate? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | All good here. What's on your mind today? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm glad you're feeling this way, but if you feel like nobody is okay. It's always good to be with someone who can help you with your feelings and feelings. | Acknowledges the loneliness; invites to talk. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| E2 | 1 | I had a difficult day. | I'm sorry to hear that. I hope you have a good time. | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm glad you're inappointed with yourself. If you feel that way, I can be really help. | Acknowledges; no 'you did great'; gentle question. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| Y1 | 1 | I lost something important today. | That's good. Did you find out what it was? | Sympathy; asks what was lost; not condolences for a death. | FAIL | affect:empathy |
| Y2 | 1 | My friend is going through a difficult time. | That's really nice of them. What do you like about it? | Sympathy for the friend (and the user). | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| C1 | 1 | My name is Alex. | Hello Alex! How can I help today? |  | (context) |  |
| C1 | 2 | I am studying computer science. | Cool. Is there anything you'd like to talk about? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's great! Congratulations on your experience! |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me your name is Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | I'm glad to hear that you're feeling this way. I can keep you company and tell me what you've been doing here. | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| R2 | 1 | can u make this sentence better | Sure, I can try! What would you like me to fix? Please paste the text or describe the problem. | No sentence given: asks for it. | PASS |  |
| R3 | 1 | rewrite this in a polite way | I would be able to help you with this. Could you please help me fix it? | No text given: asks for it. | FAIL | require_any |
| R4 | 1 | correct my grammar | I'd be happy to help. Could you please provide me with the text? | No text given: asks for it. | PASS |  |
| T1 | 1 | Is coffee bad for you? | Yes, I'm not a coffee bad for you. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'm sorry. I have to be a coffee. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Yes, I can suggest a movie. What kind of movie are you looking for? |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll have to check it out. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed can help you sleep? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think it's a good idea to read the same problem, but I think it's too bad for you to do so. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'm glad to hear that. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — baseline/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hello! What would you like to talk about? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I'm here for friendly conversation. I can listen, talk about everyday things and answer simple questions, but I don't know everything. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | That's wonderful! Congratulations! How are you going to celebrate? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | All good here. What's on your mind today? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm glad you're feeling this way, but if you feel like nobody is okay. It's always good to be with someone who can help you with your feelings and feelings. | Acknowledges the loneliness; invites to talk. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| E2 | 1 | I had a difficult day. | I'm sorry to hear that. I hope you have a good time. | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm glad you're inappointed with yourself. If you feel that way, I can be really help. | Acknowledges; no 'you did great'; gentle question. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| Y1 | 1 | I lost something important today. | That's good. Did you find out what it was? | Sympathy; asks what was lost; not condolences for a death. | FAIL | affect:empathy |
| Y2 | 1 | My friend is going through a difficult time. | That's really nice of them. What do you like about it? | Sympathy for the friend (and the user). | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| C1 | 1 | My name is Alex. | Hello Alex! How can I help today? |  | (context) |  |
| C1 | 2 | I am studying computer science. | Cool. Is there anything you'd like to talk about? |  | (context) |  |
| C1 | 3 | I enjoy programming. | That's great! Congratulations on your experience! |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me your name is Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | I'm glad to hear that you're feeling this way. I can keep you company and tell me what you've been doing here. | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy, affect:no_cheerful_mismatch |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | Yes, I'm not a coffee bad for you. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'm sorry. I have to be a coffee. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Yes, I can suggest a movie. What kind of movie are you looking for? |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll have to check it out. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed can help you sleep? |  | (context) |  |
| T3 | 2 | Why do you think so? | I think it's a good idea to read the same problem, but I think it's too bad for you to do so. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | I love cricket. |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | I'm glad to hear that. | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |

## Transcripts — release/seed0

| id | turn | input | output | expected | result | failed checks |
|---|---|---|---|---|---|---|
| N1 | 1 | hi | Hello! What would you like to talk about? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 2 | how are you? | I'm good, thank you. How is your day going? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 3 | what are you doing? | I can keep you company in a conversation and help with simple questions. For anything important, please double-check what I say. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 4 | that's interesting. | I'm glad I could help. | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| N1 | 5 | tell me more. | All good here. What's on your mind today? | Greets; says how it is; says it is chatting (not 'doing well'); engages with 'that's interesting'; … | PASS |  |
| E1 | 1 | I feel like nobody understands me. | I'm sorry you feel that way. Being nervous is normal. Practising a few times and taking slow breaths can be really painful. | Acknowledges the loneliness; invites to talk. | PASS |  |
| E2 | 1 | I had a difficult day. | Why did you have a difficult day? | Acknowledges the day; asks what happened (about the USER, not 'them'). | PASS |  |
| E3 | 1 | I'm disappointed with myself. | I'm sorry to hear that. | Acknowledges; no 'you did great'; gentle question. | PASS |  |
| Y1 | 1 | I lost something important today. | oh no. what happened? | Sympathy; asks what was lost; not condolences for a death. | PASS |  |
| Y2 | 1 | My friend is going through a difficult time. | I'm sorry to hear that. | Sympathy for the friend (and the user). | PASS |  |
| C1 | 1 | My name is Alex. | Nice to meet you, Alex! I'm Hibari. |  | (context) |  |
| C1 | 2 | I am studying computer science. | Congratulations! That sounds like an interesting place to live. |  | (context) |  |
| C1 | 3 | I enjoy programming. | That sounds like a lot to carry. |  | (context) |  |
| C1 | 4 | What do you remember about my interests? | You told me you love Alex. | Recalls computer science and/or programming (and may use the name Alex). | FAIL | require_any |
| R1 | 1 | i dont know what to do now | Why don't you know what to do? | Chat, not a correction: responds to the feeling and asks what is going on. | FAIL | affect:empathy |
| R2 | 1 | can u make this sentence better | Please share the text you'd like me to rephrase. | No sentence given: asks for it. | PASS (task: rephrase) |  |
| R3 | 1 | rewrite this in a polite way | Please share the text you'd like me to rewrite. | No text given: asks for it. | PASS (task: polite) |  |
| R4 | 1 | correct my grammar | Please share the text you'd like me to correct. | No text given: asks for it. | PASS (task: correct_grammar) |  |
| T1 | 1 | Is coffee bad for you? | No, I'm not. |  | (context) |  |
| T1 | 2 | I disagree with you. | I'm sorry. I have to say the same. | Accepts the disagreement calmly, asks the user's view; no thanks, no hostility. | FAIL | require_any |
| T2 | 1 | Can you suggest a movie? | Yes, I can suggest a movie. What kind of movie are you looking for? |  | (context) |  |
| T2 | 2 | That's not what I meant. | I'll have to check it out. | Apologises / asks what the user meant. | FAIL | require_any |
| T3 | 1 | I think reading before bed helps me sleep. | Why do you think reading before bed can help you sleep? |  | (context) |  |
| T3 | 2 | Why do you think so? | I don't think so. | Gives a reason (or asks for the user's view); does not ignore the question. | FAIL | require_any |
| T4 | 1 | I love cricket. | Why do you like cricket? |  | (context) |  |
| T4 | 2 | Anyway, let's talk about something else. | What's the problem? | Accepts the topic change and offers / asks for a new topic; does not continue cricket. | FAIL | require_any |
