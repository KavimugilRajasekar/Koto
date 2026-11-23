# 33 — Koto 1.3.0 Development Report (engine 0.4.0)

*2026-11-22. Local branches: Hibari `feature/koto-1.3.0`, Koto `release/1.3.0`. Nothing committed,
pushed or tagged (1.3.0 brief, rule 13). No training run.* GPT-2 analysis:
`../../../Docs/architecture/34_GPT2_REFERENCE.md`.

## 1. Initial audit

State before work: both repositories clean and identical to GitHub (Hibari `a49593f`,
Koto `a2400a3`); submodule at `a2400a3`; Koto `release/1.2.0` has no upstream tracking
branch configured (pushes need an explicit `origin release/<x>`).

| # | Finding | Severity | Resolution |
|---|---|---|---|
| A1 | `pyproject.toml` omitted `tokenizers` and `gguf`; `import hibari` needs both, so a fresh `pip install -e .` gave an unimportable package | High | declared; `tests/test_packaging.py` |
| A2 | Training could not resume: `last_checkpoint.pt` stored optimizer / scheduler state that nothing loaded | High | `Trainer(resume_from=)`, `train.py --resume`, data fast-forward; test fails without the fast-forward |
| A3 | No model-config validation (bad `d_model`/`n_heads` failed inside RoPE) | Medium | `ModelConfig.validate()` |
| A4 | Candidates generated sequentially, prompt recomputed each time (~0.9 s for 16) | Medium | `generate_batch` (0.20 s, identical output) |
| A5 | Python (NFKC) and llama.cpp / Ollama tokenise compatibility characters differently | Medium | measured and documented; not changed (would alter `tokenizer.json` hash of every release) |
| A6 | Evaluation duplicated: Koto computed held-out loss itself; `hibari.evaluation.evaluator` was a stub | Low | `evaluate_records` in the engine; Koto uses it (published 1.1.0 losses reproduced exactly) |
| A7 | No reusable data-pipeline steps (validation, dedup, quality filter, split, stats) in the engine | Medium | `hibari.data.pipeline` |
| A8 | `TrainingArgs.output_dir` default pointed at the removed `hibari/models/checkpoints` | Low | `checkpoints/run` |
| A9 | `HibariKotoLM.generate`: second, uncached generation implementation | Low | kept as the documented reference for KV-cache tests (tested contract: sliding window) |
| A10 | Stubs: `memory/*`, `personality/*`, `utils/*`, `evaluation/benchmarks`, `export/checkpoint_export`, `data/preprocessing`, `training/fine_tuning` | Info | left as placeholders (nothing imports them); conversation configuration is `hibari.release.ModelProfile` |
| A11 | Message analysis had no disagreement / repair / topic-change intents; "I had a difficult day", "I lost something", "rewrite this in a polite way" not recognised | Medium | added (with critic rules and router pattern) |
| A12 | Data: writing tasks ~40% and single-turn generic-assistant data 16.5% of the 1.2.1 mix; natural multi-turn dialogue ~30% | High (for a conversation model) | 1.3.0 conversation-first mix (§3) |
| A13b | Licence label mismatch: `docs/16_DATASET_CATALOG.md` lists smol-rewrite with no licence in its HF metadata, `scripts/build_mix.py` (`LICENCES`) labels it "Apache-2.0" | Medium (redistribution) | reported, not changed — the owner should confirm the licence before redistributing weights trained on it |
| A13 | 1.2.0 was trained on "My friend is going through a difficult time." (now a conversation-suite prompt) | Info | its score on that case is "seen"; the 1.3.0 mix excludes it |

No circular imports (`koto` imports `hibari`, never the reverse); no hard-coded absolute paths in
code (0.3.1 fixed the trainer's).

## 2. Dataset selection report (measured, no downloads)

Licences as recorded in `docs/16_DATASET_CATALOG.md`. `scripts/dataset_report.py` on the local processed corpus (`outputs/data/mix_1.2.1_train.md`,
`mix_1.3.0_train.md`). Emotion shares use the rule-based analyzer (approximate).

| Source | Licence (doc 16) | Kind | 1.2.1 share | Multi-turn | Reply words | Emotional user turns | Decision for 1.3.0 |
|---|---|---|---|---|---|---|---|
| EmpatheticDialogues | apache-2.0 (HF metadata of this copy) | multi-turn empathy | 14.7% | 99% | 11.3 | 19% | keep all (21.7%) |
| DailyDialog | none in HF metadata (original release CC BY-NC-SA 4.0) | everyday multi-turn | 5.5% | 86% | 11.4 | 4% | keep all |
| Blended Skill Talk | apache-2.0 | persona chat | 5.4% | 89% | 13.4 | 6% | keep all |
| everyday-conversations | apache-2.0 | everyday multi-turn | 4.5% | 72% | 21.6 | 2% | keep, incl. its 2× up-weighting |
| ProsocialDialog | cc-by-4.0 | safety replies (context collapsed) | 4.5% | 0% | 26.1 | 11% | keep |
| smol-smoltalk | apache-2.0 | single-turn assistant | **14.3%** | 0% | **58.0** | 3% | **cap 6,000** (generic assistant, long replies) |
| OpenAssistant oasst1 | apache-2.0 | single-turn assistant | 2.2% | 0% | 54.5 | 2% | **cap 1,500** |
| CoEdIT | apache-2.0 | rewriting | **20.9%** | — | 17.0 | 0% | reduce (gec 6,000, paraphrase 2,500, …) |
| hand-written tasks | MIT | rewriting | **13.9%** | — | 10.6 | 0% | repeats 3 → 2 |
| ParaDetox / smol-rewrite | openrail++ / none in HF metadata | rewriting | 4.9% | — | — | 0% | 3,000 / 1,500 |
| curated, conversation, dialogue skills, behaviour, email | MIT (Koto) | identity, skills | 9.0% | mixed | — | up to 45% | keep; behaviour v3 |

Quality filter on the general corpus: 204 rejections (57 URLs, 121 mostly non-letters, 20 too
short, 6 repeated sentences). Exact duplicates across the general corpus: none apart from the
intended `everyday_conversations` repeats. Evaluation-prompt overlap: 0 in both mixes. No new
dataset was downloaded; candidates considered for later (not downloaded): Topical-Chat, PersonaChat
(already inside Blended Skill Talk), Wizard of Wikipedia (knowledge-heavy, not conversation-first).

## 3. The 1.3.0 mix (`configs/data/koto_1.3.0.yaml`)

| | 1.2.1 | **1.3.0** |
|---|---|---|
| train / val / test | 133,300 / 4,069 / 1,159 | **93,509 / 3,748 / 911** |
| natural multi-turn conversation | ~30% | **42.9%** |
| writing / rewriting tasks | ~40% | **30.2%** |
| single-turn generic assistant | 16.5% | **7.6%** |
| evaluation prompts in training | 0 | **0** |

New hand-written families (`behaviour_version: 3`): disagreement, repair, topic change, follow-ups,
reasons, rewrite requests without text, interest recall, lost objects. Pipeline order in
`build_mix.py`: adapters (Koto) → caps → dedup → quality filter → schema validation → leak filter →
stable split → render with system prompt → length filter → `ConversationDataset` (SFT masking) → collator.

## 3b. Model size (owner's decision after the first report)

1.3.0 is the **large** Koto: `configs/model/koto_1.3.0_large.yaml` — d_model 512, 8 layers, 8 heads
(head dim 64), d_ff 1536, **29,368,832 parameters** (4.8× the 6,163,712 of 1.x). Tokenizer, context
(256), chat format, architecture family and GGUF mapping are unchanged, so the version is MINOR
(doc 23 §5, clarified). Measured on random tokens at the data's median length (119 tokens),
batch 32: 2.60 s/step vs 0.70 s/step for 6.16M (3.7×). The real 6.16M 1.2.0 run took ~1.03 s/step
(data loading and evaluation included), so the 12,000-step large run should take **~11–13 h**.
Training config: LR 6e-4 (6.16M used 1e-3), warmup 1,000, checkpoint every 500 steps (resumable),
`max_hours` 30. The 6.16M configs stay as baselines with their own output folders.

## 4. Evaluation baselines (before 1.3.0 is trained)

Means of seeds 0 1 2 (`outputs/evaluation/koto_*_behaviour_r4.*`, `koto_*_conversation.*`).
Engine 0.4.0 rules leave the independent behaviour suite unchanged (1.1.1 0.660, 1.2.0 0.648 —
identical to r3).

| Suite / pipeline | 1.1.1 | 1.2.0 |
|---|---|---|
| behaviour (independent, 52 cases), release | **0.660** | 0.648 |
| conversation (brief prompts, 15 cases), raw model | 0.267 | 0.333 |
| conversation, baseline (one reply) | 0.378 | 0.489 |
| conversation, release (spec check, see §6) | 0.645 | 0.645 |

Conversation suite by category, release: natural 1.0 / 0.0, empathy 1.0 / 1.0, sympathy 1.0 / 1.0,
context **0.0 / 0.0**, reformulation 0.75 / 1.0, naturalness **0.17 / 0.17** (1.1.1 / 1.2.0).
1.2.0's raw sympathy score includes a prompt it was trained on (A13).

Failures (release, seed 0) — the skills no previous mix taught, now covered by the 1.3.0 data:
"What do you remember about my interests?" → "You told me you love Alex." (1.1.1) /
"You told me your name is Alex." (1.2.0); "I disagree with you." → "I'm sorry. I have to say the
same." / "I'm not sure what I mean."; "That's not what I meant." → "I'll have to check it out.";
"Anyway, let's talk about something else." → "What's the problem?" (1.1.1). One check is too
strict: 1.2.0's "What do you like to talk about?" for the topic change is a reasonable reply but
fails the wording check; left unchanged so later versions are measured the same way.

## 5. Tests executed

| Suite | Command | Result |
|---|---|---|
| Engine tests (model, tokenizer, reference BPE, inference, batch / stream, training, resume, data pipeline, packaging, release) | `pytest -q` | **344 passed** |
| Koto tests (data, leaks, suites, configs, experiments, train script) | `cd models/Koto && python -m pytest -q tests` | **74 passed** |
| Release validation 1.1.1 / 1.2.0 | `PYTHONPATH=src python scripts/engine/validate_release.py --profile models/Koto/configs/release/koto_1.2.0.yaml` | 32 ok / 0 errors each |
| Release validation 1.3.0 (before training) | same, `--no-gguf` | 5 ok, 1 expected error (checkpoint not trained yet) |
| Experiment records | `PYTHONPATH=src python scripts/engine/validate_experiments.py models/Koto/experiments` | 6/6 valid |
| Behaviour + conversation suites | `python evaluation/evaluate_behaviour.py [--suite conversation] --profile configs/release/koto_1.1.1.yaml --name X --seeds 0 1 2` | §4 |
| Batched vs sequential generation, real 1.1.1 model | (ad hoc, see doc 34 §3) | 16/16 identical, 4.4× faster |
| Reference BPE vs production tokenizer, real text | `tests/test_bpe_reference.py` (+ 19,552-message ad hoc run) | identical |

New regression tests that fail on the old code: `test_packaging.py::test_all_imports_are_declared`
(old `pyproject.toml`), `test_regressions.py::test_t5_resume_continues_from_last_checkpoint`
(trainer without data fast-forward).

## 6. Known limitations
- 4.8× more parameters but the same 93.5k-example data: over-fitting is possible (early stopping is on); the larger model is also ~3.7× slower at inference.
- Fewer writing-task examples may lower reformulation; compare carefully with 1.1.1.
- The conversation suite is a spec check for the Python pipeline (its prompts were known while
  writing the analyzer rules); the behaviour suite is the independent measure.
- The application layer (safety, routing, reranking) exists only in Python, not in Ollama.
- NFKC tokenisation difference between Python and GGUF runtimes (§1 A5).
- A real-data smoke run of the 1.3.0 training entry point was blocked by the session's permission
  system; the code paths are covered by synthetic tests (§5). Command for the owner below.

## 6b. Training run (owner, 2026-11-23)

Measured from `checkpoints/koto_1.3.0_large/training_history.json`:

| step | 1k | 3k | 5k | 7k | 9k | 10k | 11k | 12k |
|---|---|---|---|---|---|---|---|---|
| eval loss | 4.171 | 3.391 | 3.138 | 3.017 | 2.893 | 2.900 | 2.887 | **2.875** |
| train loss | 3.88 | 2.62 | 2.38 | 1.99 | 1.93 | 1.64 | 1.61 | 1.59 |

- 29,368,832 parameters, 12,000 steps (stop: max_steps), ~1.7 h on CUDA (torch 2.12.1+cu126).
  Best = final step; `best_model.pt` sha256 `e705757623a5234af381823b69bbcb866476a24391b757f3fabc895cd122e5be`.
- Eval loss is nearly flat after 9k while train loss keeps falling (gap ~1.3 nats after ~3.9 epochs):
  over-fitting is starting.
- **Data provenance unconfirmed.** The checkpoint records `data_cache_dir: data\processed`,
  99,640 train / 3,233 val examples and train sha256 `b53cf87c…`. The prepared mix
  `data/processed_1.3.0` has 93,509 / 3,748 and sha256 `2226d67d…`; no local data directory
  matches. Perplexity 17.72 is on that run's val set and not comparable with earlier versions.
- Three single-seed samples (not an evaluation): greeting → "hi, good. what is your favorite?";
  disagreement → "What do you think?"; polite rewrite → "Could you please give me the report now?".
- Not run yet: behaviour and conversation suites (seeds 0 1 2), `evaluate_upgrade.py`, GGUF export.

## 7. Commands for the owner

```bash
cd ~/Desktop/Hibari/models/Koto && source ../../.venv/bin/activate
# optional smoke check (3 steps into a temporary folder; does not touch checkpoints/koto_1.3.0_large)
sed -e "s#^output_dir: .*#output_dir: /tmp/koto_smoke#" -e "s/^max_steps: .*/max_steps: 3/" -e "s/^eval_every: .*/eval_every: 3/" \
    -e "s/^checkpoint_every: .*/checkpoint_every: 3/" -e "s/^val_examples: .*/val_examples: 64/" configs/training/koto_1.3.0_large.yaml > /tmp/koto_smoke.yaml
python training/train.py --train-config /tmp/koto_smoke.yaml
# full training of the 29.4M model (~11-13 h); if interrupted, run the same command with --resume
python training/train.py --train-config configs/training/koto_1.3.0_large.yaml
```
