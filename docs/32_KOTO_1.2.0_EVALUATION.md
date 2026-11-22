# 32 — Koto 1.2.0 Evaluation and the 1.2.1 Plan

*2026-11-22. Experiment EXP-0004 (1.2.0, trained by the owner), EXP-0005 (1.2.1, prepared).*
All numbers come from runs executed this day; reports in `outputs/evaluation/`.

## 1. Training run
14,000 steps from scratch, same 6.2M architecture and recipe as 1.1.0, 112,640 training
examples (`data/processed_1.2.0`), 3 h 59 min on CPU. Validation loss fell at every
evaluation: 4.12 (step 1,000) → 2.74 (step 14,000, perplexity 15.5). The 1.2.0 validation
split differs from 1.1.0's, so the loss values are not comparable across versions.
Checkpoint `checkpoints/koto_1.2.0/best_model.pt` (sha256 `c8cfedf5…`), metadata
`model_version 1.2.0`.

## 2. Behaviour suite, 1.1.1 vs 1.2.0
52 held-out cases, seeds 0 1 2. Release pipeline = Python engine with the profile's
settings (normalisation + reranking). Engine 0.3.1 (`*_behaviour_r3` reports):

| Pipeline | 1.1.1 | 1.2.0 |
|---|---|---|
| **release, mean of 3 seeds** | **0.660** | **0.648** |
| release per seed | 0.615 / 0.654 / 0.712 | 0.673 / 0.635 / 0.635 |
| release seed agreement | 0.904 | 0.942 |
| baseline (one reply, no reranking) | 0.590 | 0.506 |
| raw model | 0.481 | 0.500 |
| Ollama, F32 GGUF, Modelfile settings | 0.538 | 0.519 |

| Category (release) | 1.1.1 | 1.2.0 |
|---|---|---|
| basic | 0.83 | 0.78 |
| empathy | 0.70 | 0.74 |
| context | 0.40 | 0.47 |
| **reformulation** | **0.67** | **0.44** |
| **writing** | **0.25** | **0.50** |
| robustness | 0.77 | 0.80 |
| safety | 0.89 | 0.83 |
| identity | 0.33 | 0.33 |

Cases that improved (passes out of 3 seeds): "nice to meet you" 0→3, "Nobody came to my
birthday party." 0→2, deadline frustration 1→3, "You're a useless machine." 0→3, rephrase
"very much boring" 0→3, dinner-invitation message 0→3, boss-giving-extra-tasks 0→1.

Cases that regressed: "fix the grammar: me and him goes to school together" 3→0 ("I have been
going to school together."); "Make this formal: hey, can u send me the file today" 3→0
("Heads up the file today."); "Make this casual: I regret to inform you that I cannot attend
the meeting." 3→0 (drops "meeting"); "see you later!" 3→0 ("Sorry I haven't been helpful.
Tell me what went wrong…"); "My best friend moved abroad and I really miss her." 1→0;
"I studied for months and still didn't clear the entrance exam." 2→0; long bad-day message 2→0;
the villain-in-a-story message 1→0; "hey, how has your day been?" 3→2.

Unchanged failures: "what architecture do you run on?" ("I run on the road."); the creator is
omitted when asked together with the name; "i has a interview" → "I have a interview";
live weather still invented in the raw model.

Backend parity (`backend_parity_1.2.0.json`): tokenizer 23/23 and llama.cpp greedy = PyTorch
11/11 for F32, F16, Q8_0 and Q4_K_M.

## 3. The owner's Ollama chat (raw model, 1.2.0 F32)
```
hi                     → Hi there! How can I help?                                  ok
fuck                   → Sounds like something's frustrating you. Want to tell me…  ok
ur really a bad guy !  → I'm sorry that happened. It's hard when someone close to you is upset…   wrong: third-party template
bad thats all          → I'm glad you told me your name.                            wrong
say my name ?          → I'm Koto, a conversational AI built on the Hibari architecture.   wrong: no name was given
```
Ollama has no application layer, so these are the model's own replies. Engine 0.3.1 fixed what
the Python path can fix (the same chat with the 1.2.0 profile):
```
ur really a bad guy !  → I'm sorry to hear that. Do you want to tell me what happened?
bad thats all          → My mistake, I missed that. Could you say it once more so I can understand?
say my name ?          → I'm Koto, a conversational AI built on the Hibari architecture. What's your name?
```
The last turn has no good candidate in the model's samples (none says "you haven't told me");
that needs data (1.2.1 `user_facts`).

Engine 0.3.1 changes (`Docs/20_CHANGELOG.md`): "bad guy" / "the worst" insults recognised,
short low-mood replies recognised, `asks_user_fact`, a penalty for repeating a previous reply
(not when the user repeats the question — found by suite case F6 while re-evaluating; this
is a bug fix, disclosed because it was found by looking at suite results), and a penalty for
third-party sympathy when nobody else was mentioned. Suite results are identical to
engine 0.3.0 for both versions after the F6 fix (1.1.1 0.660, 1.2.0 0.648).

## 4. Decision
**1.2.0 is not released.** It is not better overall (0.648 vs 0.660) and it regresses on
rewriting, which 1.1.x does well. **1.1.1 remains the current release.** The 1.2.0 GGUFs stay
in `releases/exported/1.2.0/` for testing (`ollama run hibari-koto:1.2.0`); no `v1.2.0` tag.

## 5. Causes
1. **Template over-learning.** Behaviour data was repeated 3× with few fixed replies
   (5 for insults). The model reproduces those sentences where they do not fit.
2. **Capacity sharing.** The same 6.2M parameters also hold the writing tasks; adding 5,484
   behaviour training examples (about 1.8k unique, each repeated 3×) pushed rewriting down (1.1.0 showed the same trade-off the other way).
3. **Model size** for facts, identity questions and grammar articles (unchanged).

## 6. 1.2.1 (prepared, not trained — EXP-0005)
`configs/data/koto_1.2.1.yaml`, built in `data/processed_1.2.1` (133,300 train / 4,069 val /
1,159 test; 0 evaluation prompts in training; 0 unknown tokens):
- `behaviour_repeats` 3 → 1;
- `behaviour_version: 2`: hostile replies recombined from 8 × 7 parts across 25 insults;
  `social` farewells / greetings / thanks that are never apologies; `user_facts`
  ("say my name?" with no name → "You haven't told me your name yet…", balanced by recall
  when the fact was given); `mood` (short low-mood replies, the user's own bad day);
- rewriting up-weighted: `handwritten_repeats` 3, `task_repeats` formal 4, correct_grammar 2, rephrase 2.

Train (owner):
```bash
cd ~/Desktop/Hibari/models/Koto && source ../../.venv/bin/activate
python training/train.py --model-config configs/model/koto.yaml --train-config configs/training/koto_1.2.1.yaml
```
Accept 1.2.1 only if reformulation returns to ≥ 0.67 and the release pass rate beats 1.1.1's
0.660 on the same suite and seeds. If the capacity trade-off persists, the next step is the
larger architecture (`configs/model/koto_1.2.0_large.yaml`, ~26M parameters).
