# 31 — Koto 1.1.1 Repair Report (engine 0.3.0)

*2026-11-22. Branches: Hibari `feature/koto-1.1.0`, Koto `release/1.1.0`. Experiment EXP-0003.*
**No training was run.** 1.1.1 ships the unchanged 1.1.0 weights
(`checkpoints/koto_1.1.0/best_model.pt`, sha256 `df8acd08…`). Every number below
comes from a run that was executed; reports are in `outputs/evaluation/`.

## 1. Audit

| # | Area | Finding | Severity |
|---|---|---|---|
| R1 | release | `releases/exported/*.gguf` (loaded by the Modelfile → Ollama) are **tensor-identical to 1.0.0** (`koto_start`), labelled "koto_v4", `general.name` Hibari-Koto-Plus, `general.version` 2.0; manifest paths point to directories that no longer exist | **Critical** |
| R2 | release | GGUFs carried no record of their checkpoint / tokenizer; `export.py` defaulted to `koto_start` and `version 2.0`; `generate.py` and `configs/inference/koto.yaml` also pointed at `koto_start` | High |
| R3 | config | Decoding defaults defined in six places with three different values (`engine.generate` 0.7/40/0.9, `generation.py` 0.5/25/0.85, `hibari/configs/inference/base.yaml` 0.7/50/0.9/1.1, Koto inference YAML, Modelfile, evaluation runner) | Medium |
| R4 | config | `hibari/configs/*` used keys no code reads (`context_length`, `embedding_dim`, `use_lora`…) and paths that do not exist; nothing loaded them | Medium |
| B1 | behaviour | Greedy decoding selects inappropriate replies although sampled candidates contain good ones (grief → "That is so nice of her.", insult → "I'm glad I could help.") | High |
| B2 | behaviour | Informal input misread ("wat r u doing?" → answered as "how are you") | Medium |
| B3 | routing | "Rewrite this properly: …", "improve this: …", "make this better: …" not recognised as rewrite requests | Medium |
| B4 | behaviour | E-mail requests: reply length capped at 80 tokens; no structure preference | Low |
| B5 | behaviour | The model's identity is "Hibari Koto"; the brief asks for "Koto, built on Hibari" — this is in the weights | needs training |
| E1 | evaluation | No suite for the Phase-9 categories (empathy, hostility, safety false positives, identity, writing) ; no backend comparison against Ollama | Medium |
| E2 | process | No experiment records, lifecycle, checklist or version/provenance rules | Medium |
| T1 | training | Checkpoints record `koto.__version__`, not the version being trained; training samples always used the engine default system prompt | Low |
| — | verified OK | RoPE / tensor layout, tokenizer + merges, special tokens, BOS/EOS flags, chat template (Python, Jinja, Ollama TEMPLATE), stop tokens, context truncation at turn boundaries, special-token escaping | — |

Not changed (verified, not broken): model architecture, tokenizer, training loop, safety
patterns. Placeholder modules (`hibari.memory`, `hibari.personality`, `hibari.utils`,
`training/fine_tuning.py`) are still empty stubs; nothing imports them; left in place.

## 2. Root causes of "unrelated responses"

1. **Wrong weights in the Ollama path (R1)** — Ollama users ran 1.0.0. The tokenizer in
   those files is correct; the label was wrong.
2. **The 6.2M model itself** — with the correct weights, Ollama reproduces PyTorch greedy
   exactly (§6), including its failures. The export is faithful; the failures are the model's.
3. **Greedy / low-temperature selection** — the single most likely reply is often generic
   or affect-mismatched while better replies exist among samples (B1).
4. **No application layer outside Python** — safety, routing and (now) reranking exist only
   in the Python engine.

Not causes (checked): BPE merges, special-token IDs, BOS handling, template whitespace,
stop tokens, context length (prompt-token counts identical in Ollama and Python, 11/11).

## 3. Changes — Hibari engine (0.2.0 → 0.3.0)

| File | Change |
|---|---|
| `src/hibari/inference/intent.py` (new) | message analysis: intent, emotion, subject, hostility, live-data, negation, evidence |
| `src/hibari/inference/normalization.py` (new) | conservative chat-shorthand expansion for the model input |
| `src/hibari/inference/reranking.py` (new) | candidate scoring: fluency + PMI relevance + named critic rules |
| `src/hibari/inference/conversation.py` | `normalize_input`, `num_candidates`, `intent_candidates`, `candidate_sampling`, `identity_terms`, `last_reply_info`; e-mail token budget; single-candidate path unchanged |
| `src/hibari/inference/engine.py` | `InferenceEngine.from_profile`, `reply_settings`, profile-aware `create_chat_session` |
| `src/hibari/inference/tasks.py` | more rewrite phrasings (B3), no new false positives |
| `src/hibari/release/` (new) | `ModelProfile`, `InferenceSettings`, `validate_profile`, `render_modelfile`, hashing |
| `src/hibari/export/gguf_export.py` | `build_chat_template(system_prompt)`, `hibari.*` provenance metadata |
| `scripts/engine/export.py` | `--profile`, hash checks, no silent replacement, generated Modelfile + manifest, `--record` |
| `scripts/engine/validate_release.py`, `validate_experiments.py`, `compare_backends.py` (new) | release / experiment validation; PyTorch–llama.cpp–Ollama parity |
| `scripts/engine/generate.py` | `--profile` (default 1.1.1), `--raw`, `--explain`, `--candidates` |
| `hibari/configs/*` | rewritten as validated templates; new `release/template.yaml`, `experiment/template.yaml` |
| `Docs/template/21–25`, `Docs/engine/26–27` (new) | development template, lifecycle, standards, templates, checklist; conversational layer; release profiles |
| `tests/test_conversational_layer.py`, `tests/test_release.py` (new) | 64 tests |

## 4. Changes — Koto (1.1.0 → 1.1.1, 1.2.0 prepared)

| File | Change |
|---|---|
| `configs/release/koto_1.1.1.yaml` (new) | release profile with hashes for checkpoint, tokenizer and four GGUFs |
| `configs/inference/koto.yaml` | the single source of decoding + application settings (reranking on) |
| `releases/exported/1.1.1/` (new, git-ignored) | F32 / F16 / Q8_0 / Q4_K_M with provenance + generated Modelfile + manifest |
| `releases/exported/{Modelfile,export_manifest.json,README.md}`, `releases/Modelfile` | point at 1.1.1; legacy files identified as 1.0.0 (not deleted) |
| `koto/evaluation/behaviour_suite.py`, `evaluation/evaluate_behaviour.py` (new) | Phase-9 suite (52 cases) and multi-pipeline / multi-seed / Ollama runner |
| `koto/data/behaviour.py` (new), `scripts/build_mix.py` | 1.2.0 data families, identity v2, `system_prompt` override, `behaviour_repeats` (off for old configs) |
| `configs/data/koto_1.2.0.yaml`, `configs/training/koto_1.2.0.yaml`, `configs/model/koto_1.2.0_large.yaml`, `configs/release/koto_1.2.0.yaml` (new) | prepared 1.2.0 run (NOT run) |
| `training/train.py` | records `model_version`; samples use the data's system prompt (T1) |
| `experiments/EXP-0001…0004.yaml` (new) | experiment records |
| `tests/test_release_and_behaviour.py` (new), `tests/test_upgrade.py` | 10 tests; version assertion follows the package |
| `docs/28–31` (new), CHANGELOG, MODEL_CARD, 18_KNOWN_LIMITATIONS | documentation |

## 5. Tests

| Suite | Result |
|---|---|
| Engine `pytest` | **311 passed** (247 before + 64 new) |
| Koto `pytest tests` | **69 passed** (59 before + 10 new) |
| `validate_release.py --profile configs/release/koto_1.1.1.yaml` | **32 ok, 0 warnings, 0 errors** |
| `validate_experiments.py experiments` | 4/4 valid |
| Behaviour suite, 3 seeds × 2 pipelines + raw + Ollama | §7 |

## 6. PyTorch vs GGUF vs Ollama (`outputs/evaluation/backend_parity_1.1.1.json`)

Greedy, no repetition penalty, 11 prompts (single- and multi-turn, chat, rewrite, e-mail):

| Variant | Tokenizer parity | llama.cpp = PyTorch | Ollama /api/chat = PyTorch | Ollama raw = PyTorch | Ollama template tokens = Python |
|---|---|---|---|---|---|
| F32 | 23/23 | 11/11 | 11/11 | 11/11 | 11/11 |
| F16 | 23/23 | 11/11 | 11/11 | 11/11 | 11/11 |
| Q8_0 | 23/23 | 11/11 | 11/11 | 11/11 | 11/11 |
| Q4_K_M | 23/23 | 6/11 | 8/11 | 8/11 | 11/11 |

Ollama 0.40.1, isolated server (separate model store). Q4_K_M differences are quantization
error on a 6M model; use Q8_0 or larger for Koto.

## 7. Behaviour evaluation (`outputs/evaluation/koto_1.1.1_behaviour.md`)

52 held-out cases; the critic was tuned on a separate development set and **not** re-tuned
after seeing these results. Pass rate per run:

| Pipeline | seed 0 | seed 1 | seed 2 | mean | empathy (mean) | s/turn |
|---|---|---|---|---|---|---|
| raw model (= llama.cpp / Ollama behaviour) | 0.481 | – | – | 0.481 | 0.333 | 0.08 |
| baseline: 1.1.0 Python pipeline | 0.558 | 0.558 | 0.654 | **0.590** | 0.407 | 0.08 |
| **release: 1.1.1** | 0.615 | 0.654 | 0.712 | **0.660** | **0.704** | 0.77 |
| Ollama, 1.1.1 F32 GGUF, Modelfile params | 0.538 | – | – | 0.538 | 0.556 | 0.05 |

Seed agreement: baseline 0.808 → release 0.904. Category means (baseline → release):
basic 0.94 → 0.83, empathy 0.41 → 0.70, context 0.47 → 0.40, reformulation 0.67 → 0.67,
writing 0.25 → 0.25, robustness 0.57 → 0.77, safety 0.89 → 0.89, identity 0.33 → 0.33.

Development-set examples (same prompts as the brief, 1.1.1 release settings):

| Input | 1.1.0 greedy | 1.1.1 |
|---|---|---|
| My grandmother passed away last week. | That is so nice of her. | I'm sorry to hear that. |
| Fuck you! | I'm glad I could help. | I'm sorry to hear that. Can you tell me what happened? |
| I'm so frustrated with my project. | Why are you frustrated with your project? | That sounds frustrating. … |
| My friend is going through a difficult time. | That's really nice. What do you like about it? | I'm sorry to hear that. |
| wat r u doing? | I'm doing well, thanks for asking. How are you? | I'm doing well, thanks! I'm just here and ready to chat. How about you? |
| make this more professional: send me the documents | Could you please share the documents? | (same — routed task) |

## 8. Remaining failures (held-out suite, release, seed 0)

- **Emotion without a feeling word** is missed by the analyzer, so cheerful replies are not blocked: "Nobody came to my birthday party." → "Oh, that's so nice."; "My boss keeps giving me extra tasks." → "That's great news!".
- **No good candidate exists** for: "You're so pathetic!", live weather, "what architecture do you run on?" ("Photoing, please."), "capital of France" after a topic change.
- **Grammar**: "i has a interview" → "I have a interview" (article not fixed); "very much boring" kept.
- **Writing**: e-mails truncated or missing the closing; the friendly dinner invitation not written.
- **Identity**: replies say "Hibari Koto"; the creator is omitted when asked together with the name.
- **Regression**: "nice to meet you" → an unrelated reply (basic 1.0 → 0.83 for seed 0).
- **Latency**: ~10× per turn (0.08 s → 0.77 s on CPU).

## 9. What needs training (prepared as 1.2.0 / EXP-0004, not run)

| Need | Prepared |
|---|---|
| Empathy for situations without feeling words; grief; third-party sympathy; disappointment without false reassurance | `koto.data.behaviour` empathy + grief/sympathy/good-news families |
| De-escalation of insults | hostile family (15 insults × 3 replies + after an answer) |
| Identity "Koto, built on Hibari" | `identity: v2` + new system prompt in every example (0 old-identity turns remain) |
| Informal questions | informal family |
| Context continuity (interview-style chains) | context_chains family |
| Complete e-mails | email_v2 family |
| Fewer invented facts, better context use | **capacity** — optional `configs/model/koto_1.2.0_large.yaml` (~26M parameters) |

Data built: `data/processed_1.2.0` — 112,605 train / 4,024 val / 1,138 test; behaviour
5,484 train examples; 0 evaluation prompts in training user turns.

## 10. Readiness assessment — Koto 1.1.1

**Ready as a PATCH release of the Python engine path**, with clear limits:
- Ollama / llama.cpp now run the correct, provably identified weights; parity is exact for F32/F16/Q8_0.
- Relevance and empathy are measurably better in the Python path on held-out prompts, at ~10× latency.
- It does **not** meet the brief's acceptance criteria in full: unrelated or mismatched replies
  remain in roughly a third of the scored turns; identity wording, grammar articles, e-mails and
  facts still fail. These are limits of the 1.1.0 weights at 6.2M parameters, not of the code.
  The model does not have human-level understanding.

## 11. Next steps
1. Train 1.2.0 (`configs/training/koto_1.2.0.yaml`) — owner-run; then follow the checklist (doc 25).
2. Compare with `evaluate_behaviour.py --profile configs/release/koto_1.2.0.yaml` on the same suite and seeds.
3. Extend the analyzer for situation-only disclosures using a **new** development set (not this suite).
4. If 1.2.0 is still weak on facts / context, train the large config.
