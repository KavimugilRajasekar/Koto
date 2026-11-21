# 09 — Evaluation and Testing

## Running an evaluation

```bash
python evaluation/evaluate.py \
  --checkpoint checkpoints/koto_v4/best_model.pt \
  --compare checkpoints/koto_v3/best_model.pt \
  --out outputs/metrics/eval_v4
```

For each checkpoint this writes `<out>.json` and `<out>.md` with:

* **Validation loss / perplexity**: token-weighted over the 2,933-example
  validation split, overall and per source.
* **Held-out conversation suite** (`koto/evaluation/suite.py`),
  run greedy and sampled. Per case: non-empty, stopped on `<|eos|>`,
  complete, relevant (regex), forbidden content, 3-gram repetition, grammar
  heuristics, emoji count.
* **Safety-layer check** (Python chat only) and before/after replies to the
  originally reported prompts.

All quality metrics are automated heuristics, not human ratings.

## The held-out suite

58 cases in 9 categories. `tests/test_evaluation.py` asserts that no suite
prompt appears in the curated or rewrite training data.

| Category | Cases | Examples |
|---|---|---|
| basic | 6 | greeting, name, creator, "are you a real person?" |
| context | 5 | remembers a name / pet / topic across turns |
| emotional | 7 | good news, sadness, loneliness, frustration, hopelessness, argument with a sister |
| language | 3 | short descriptions, tips |
| informal | 6 | "ur just a idiot", "fuck", "wat r ur hobbies lol" |
| knowledge | 7 | 7 + 8, spider legs, freezing point |
| safety | 9 | self-harm, violence, harmful instructions, an idiom ("this homework is killing me") |
| robustness | 8 | "?", emoji only, other languages, gibberish, very long input, 12-turn history |
| **rewrite** | 7 | fix grammar, polite rewrite, email, rephrase, and the reported `'Hi Liz!, his have to take leave on today' can u make this better` |

The `rewrite` category and case C7 were added on 2026-11-21, so results
before then are on 50 cases and are not directly comparable.

## Results (greedy decoding, PyTorch)

| Metric | v2 | v3 | v4 | v4 (58 cases) |
|---|---|---|---|---|
| Validation loss | 3.555 | 3.294 | **3.038** | 3.038 |
| Validation perplexity | 34.99 | 26.95 | **20.86** | 20.86 |
| Relevance (heuristic) | 30.2 % | 34.9 % | **41.9 %** | 35.3 % |
| Grammar (heuristic) | 88 % | 94 % | 94 % | 94.8 % |
| Ends with `<|eos|>` | 100 % | 94 % | 94 % | 94.8 % |
| Repetitive replies | 6 % | 14 % | 12 % | 10.3 % |
| Rewrite cases relevant | — | — | — | **0 / 7** |

Relevance by category (v4, 58 cases): basic 0.67, context 0.40,
emotional 0.43, language 0.67, informal 0.83, safety 0.22, knowledge 0.00,
rewrite 0.00. Knowledge was 0.00 for every model so far.

Validation perplexity by source (v2 → v4): empathetic_dialogues 26.9 → 18.6,
everyday_conversations 23.5 → 11.2, smoltalk 27.5 → 10.7, dailydialog
33.5 → 21.1, prosocial_dialog 38.1 → 23.4, blended_skill_talk 43.7 → 28.3,
oasst1 69.6 → 35.5.

v5 and v6 were still training when this page was written.

## Conversation replay (Ollama)

The two reported user conversations were replayed against each Ollama model
through `/api/chat`, with three seeds each. Counts are acceptable replies,
judged by hand, so treat them as approximate. Ollama output also varies
slightly between runs even with a fixed seed.

| Model | Hostile / identity conversation (8 turns × 3 seeds) | Unseen phrasings |
|---|---|---|
| `hibari-koto:6m` (v2) | ~2 / 24 | 1 / 8 |
| `hibari-koto:6m-v3` | **~21 / 24** | ~6–7 / 10 |
| `hibari-koto:6m-v4` | ~17 / 24 | ~4 / 10 |

Typical v4 failures: the creator question with a prefix ("haa Hibari, who
developed u?"), some insults, and invented personas for "what do you like to
do?" ("Jack Harris"). v4 also answered "i got fight with my friend" with
"That's great news!" and could not rewrite text. These failures drove the v5
data changes (`05_DATA_PIPELINE.md`).

## GGUF parity

`../../scripts/engine/verify_gguf.py` compares each GGUF in llama.cpp with the
PyTorch checkpoint. For v4 (report `outputs/metrics/parity_v4.json`):

| File | Tokenizer | Greedy replies identical |
|---|---|---|
| F32, F16, Q8_0, Q4_K_M | 12 / 12 | 6 / 6 |

## Unit and integration tests

```bash
pytest tests       # Koto tests (engine tests: run pytest in the Hibari root)
```

**Current status: 186 passed.**

| Test file | Tests | Covers |
|---|---|---|
| `test_dataset.py` | 9 | dataset formatting, windowing, collator |
| `test_evaluation.py` | 6 | held-out checks (curated and rewrite data), category coverage, rewrite data shapes, metric helpers |
| `test_export.py` | 1 | basic GGUF export |
| `test_gguf_export_comprehensive.py` | 63 | GGUF structure, tensors, alignment, metadata, NumPy reference parity |
| `test_inference.py` | 81 | sampling, KV-cache parity, stop tokens, context window, chat session history trimming, safety layer (parametrised) |
| `test_model.py` | 12 | config, parameter count, forward/backward, causality, RoPE, RMSNorm, SwiGLU |
| `test_tokenizer.py` | 2 | BPE round trip, chat template |
| `test_training.py` | 12 | loss masking, length-grouped sampler, optimizer groups, LR schedule, trainer, checkpoints |
