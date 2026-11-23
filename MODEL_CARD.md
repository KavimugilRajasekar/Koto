# 17 — Model Card: Hibari Koto

## Model details

| Field | Value |
|---|---|
| **Name** | Hibari Koto (`Hibari-Koto`) |
| **Type** | Decoder-only autoregressive transformer, LLaMA-style |
| **Parameters** | **6,163,712 (~6.16M)** |
| **Layers / width / heads** | 6 blocks, d_model 256, 8 heads (head dim 32), SwiGLU d_ff 768 |
| **Normalisation / positions** | Pre-RMSNorm (ε = 1e-5), RoPE (θ = 10,000, adjacent-pair rotation) |
| **Context length** | 256 tokens |
| **Vocabulary** | 4,096 byte-level BPE tokens |
| **Weight tying** | input embedding = output head |
| **Training** | from scratch in PyTorch on CPU; loss on assistant tokens only |
| **Author** | Kavimugil Rajasekar |
| **Licence (code and weights)** | MIT; check the training-data licences in `16_DATASET_CATALOG.md` before redistributing |

## Versions

| Version | Checkpoint | Val ppl | Character |
|---|---|---|---|
| v2 | `koto_v2/best_model.pt` (step 3000) | 34.99 | first working Koto; weak on identity and insults |
| v3 | `koto_v3/best_model.pt` (step 2000) | 26.95 | fine-tune of v2; best at identity and hostile messages so far |
| v4 | `koto_v4/best_model.pt` (step 11000) | **20.86** | full 12k-step train; most fluent, weaker on identity |
| v5 | `koto_v5/` | — | fine-tune of v4 with writing help; training (2026-11-21) |
| v6 | `koto_v6/` | — | full train including writing help; training (2026-11-21) |
| **1.0.0** | `koto_start/best_model.pt` (= v4) | **20.86** | released; better open chit-chat |
| **1.1.0** | `koto_1.1.0/best_model.pt` (step 12000) | 22.39 | writing tasks, dialogue skills; not yet released |
| **1.1.1** | `koto_1.1.0/best_model.pt` (unchanged) | 22.39 | current: same weights + reranking, normalisation, provenance-checked GGUFs (`releases/exported/1.1.1/`) |
| 1.2.0 | `koto_1.2.0/best_model.pt` (step 14000) | — | trained 2026-11-22; identity "Koto, built on Hibari"; better writing / empathy, worse rewriting; **not released** (docs/32) |
| 1.2.1 | `koto_1.2.1/` | — | data prepared (fewer repeats, more reply variety, rewriting up-weighted); not trained; superseded by 1.3.0 |
| 1.3.0 | `koto_1.3.0_large/best_model.pt` (step 12000) | 17.72* | **29.4M parameters** (512 / 8 layers / 1536); trained 2026-11-23; training data unconfirmed (see CHANGELOG); evaluated: **not accepted** (behaviour 0.558). *own val set, not comparable |
| 1.3.1 | `koto_1.3.1_large/` | — | 1.3.0 retrain on the intended 1.3.0 mix, data fingerprint pinned, `resid_dropout 0.1`; not trained (EXP-0007) |

> The GGUFs directly in `releases/exported/` contain the **1.0.0** weights (see `releases/exported/README.md`). Use `releases/exported/1.1.1/`.

`best_model.pt` in each run folder is the checkpoint to use. The top-level
`checkpoints/best_model.pt` is an old v1 step-250 file and
should not be used.

## Intended use

* Short, friendly, emotionally supportive small talk in English.
* Simple writing help (v5 and later): fixing the grammar of a short
  sentence, rephrasing, making a message polite or formal, and drafting a
  short template email.
* Learning and research: every component (tokenizer, model, training,
  export) is implemented from scratch and documented.
* Local CPU inference via PyTorch, llama.cpp or Ollama.

## Out of scope

* Facts, advice or reasoning that matter. Knowledge-question relevance was
  0 % for every version so far.
* Mental-health support. Hibari points to crisis resources, but it is not a
  mental-health tool.
* Long documents or long conversations (256-token context).
* Users who could be harmed by a wrong reply, unless an external moderation
  layer sits in front (the GGUF has no safety layer).

## Training data

Seven conversation datasets (about 70k examples), hand-written curated
behaviour examples, and, from v5, CoEdIT, ParaDetox, smol-rewrite and a
hand-written polite / email set. See `16_DATASET_CATALOG.md` and
`05_DATA_PIPELINE.md`.

## Evaluation (v4, greedy)

| Metric | Value |
|---|---|
| Validation perplexity | 20.86 |
| Relevance (heuristic, 50-case suite) | 41.9 % |
| Grammar (heuristic) | 94 % |
| Rewrite cases (7) | 0 / 7, before writing-help training |
| GGUF parity (llama.cpp vs PyTorch) | 6/6 identical greedy replies in all 4 formats |
| Speed (Q8_0, llama.cpp, 6 threads) | ~5,000 tokens/s generation |

## Evaluation (1.1.0 vs 1.0.0, same data, greedy)

| Metric | 1.0.0 | 1.1.0 |
|---|---|---|
| Open-conversation val perplexity (old split) | **20.86** | 22.39 |
| 1.1.0 suite pass rate (routed / unrouted) | 16.7 % / 9.3 % | **53.7 % / 50 %** |
| Grammar correction cases | 1 / 5 | **5 / 5** |
| Held-out dialogue cases | 1 / 11 | 6 / 11 |
| Rewrite output-only rate | 75.9 % | 100 % |
| Legacy heuristic relevance / grammar | 35.3 % / **94.8 %** | **54.9 %** / 89.7 % |

1.1.0 still invents facts and handles emotional messages unreliably; see
`docs/19_KOTO_1.1.0_DEVELOPMENT_REPORT.md`.

Full results: `09_EVALUATION_AND_TESTING.md`. Limitations:
`18_KNOWN_LIMITATIONS.md`.

## Recommended sampling

| Parameter | Value |
|---|---|
| `temperature` | 0.5 (0 = deterministic) |
| `top_k` / `top_p` | 25 / 0.85 |
| `repetition_penalty` | 1.15 |
| stop tokens | `<|eos|>`, `<|user|>`, `<|system|>`, `<|assistant|>` |
| system prompt | `You are Hibari Koto, a friendly and calm AI companion. Keep replies short, kind and honest.` |

## Files

| Artifact | Path |
|---|---|
| Checkpoints | `checkpoints/koto_v<N>/best_model.pt` |
| Tokenizer | `tokenizer/` (`tokenizer.json`, `tokenizer_config.json`) |
| GGUF | `releases/exported/Hibari-Koto-{F32,F16,Q8_0,Q4_K_M}.gguf` (currently v4) |
| Ollama Modelfile | `release/Modelfile` (template), `releases/exported/Modelfile` |
| Data caches | `data/processed*/` |

Checkpoints, GGUFs and data caches are gitignored and exist only locally.
