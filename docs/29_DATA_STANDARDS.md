# 29 — Koto Data Standards

Sources and licences: [16_DATASET_CATALOG.md](16_DATASET_CATALOG.md). Pipeline: [05_DATA_PIPELINE.md](05_DATA_PIPELINE.md) and `scripts/build_mix.py`.

## Quality standards
- Every conversation is `[system, user, assistant, …]`, alternating, ending on an assistant turn.
- One system prompt for every example of a version (`system_prompt` in the data config); 1.2.0
  replaces the prompt inside the general corpus too.
- Assistant replies: Koto's identity, no claimed human experiences, no emojis in curated data,
  rewrite replies contain only the rewritten text.
- Hand-written families are slot templates with several phrasings per slot; replies acknowledge
  and then ask one question or offer one step (empathy), never a fixed sentence per input.
- No example is longer than `max_seq_len + 1` tokens; long conversations are windowed at turn
  boundaries, never cut inside a reply.
- Task examples: one target per (task, source); a different second target is a contradiction and is dropped.

## Preprocessing
`clean_text` (spacing, quotes), `normalize_conversation`, `window_conversation`
(`hibari.data.formatting`); offline Hugging Face cache only (`HF_HUB_OFFLINE=1`).

## Leakage prevention
- Every user prompt of the upgrade suite, the legacy suite and the behaviour suite (three or more
  words) is removed from all training sources; task sources are filtered regardless of length.
- Stable hash split (`split_of`): a source text never appears in two splits.
- `data_stats.json` reports `leak_drops`, `eval_prompts_in_train_user_turns` (must be empty) and
  `heldout_user_turns_also_in_train`.
- Tests: `tests/test_evaluation.py`, `tests/test_release_and_behaviour.py::test_behaviour_suite_held_out_from_behaviour_data`.
- Tuning prompts for decoding / the critic are kept outside the suites (doc 31 §7).

## Validation checklist (before training)
- [ ] `build_mix.py` ran into a new `out_dir` (it refuses to overwrite).
- [ ] `data_stats.json`: per-source counts as expected; `eval_prompts_in_train_user_turns == []`; `unk_tokens… == 0`.
- [ ] Every example uses the intended system prompt; no old-identity assistant turns (1.2.0: 0).
- [ ] Spot-read 20 random examples of each new family.
- [ ] Training config `data_cache_dir` = data config `out_dir`; `model_version` = release profile `weights_version`.
