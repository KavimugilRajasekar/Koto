# 08 — Fine-Tuning

Hibari fine-tunes by **continuing full training** from an existing
checkpoint on a new data mix. All 6.16M weights are updated; there is no
separate adapter. At this model size a full fine-tune of 2,500–4,500 steps
takes 45–90 minutes on CPU, so parameter-efficient methods are not needed
yet.

## Recipe

1. Edit or add training examples:
   * behaviour / identity → `koto/data/curated.py` (`INTENTS`, `MULTI_TURN`)
   * writing help → `koto/data/rewrite.py`
2. Build a mix from the local cache (the chat data is not downloaded again):
   ```bash
   python scripts/build_finetune_mix.py --dst data/processed_v5 \
     --replay 30000 --curated-repeats 4 \
     --coedit 12000 --paradetox 6000 --smol-rewrite 5000 --polite-repeats 2
   ```
   Keep general replay at 50 % or more of the mix, so the model doesn't
   forget how to chat. Keep curated examples at about 10 %: at about 4 % (v4)
   they were drowned out.
3. Train from the base checkpoint into a **new** `output_dir`:
   ```bash
   python training/train.py \
     --train-config configs/training/koto_v5.yaml \
     --data-cache-dir data/processed_v5 \
     --checkpoint checkpoints/koto_v4/best_model.pt
   ```
   Use a lower LR than from-scratch training (3e-4 instead of 1e-3) and a
   short warmup.
4. Evaluate against the base (`09_EVALUATION_AND_TESTING.md`), export, and
   load into Ollama under a new tag.

Do not reuse prompts from `koto/evaluation/suite.py` in the
training data; `tests/test_evaluation.py` fails if you do.

## Fine-tunes so far

| Run | Base | Added | Result |
|---|---|---|---|
| v3 | v2 | insults, "kill yourself", harassment, "I hate you", "what's wrong with you", creator phrasings, name prefixes, hostile multi-turn chains | val ppl 34.99 → 26.95; about 21/24 acceptable replies on the reported Ollama conversation (v2: about 2/24) |
| v5 | v4 | writing help (CoEdIT, ParaDetox, smol-rewrite, polite / email set); friend conflicts, "I have a problem", "I feel bad", "I already told you", hobbies / about you | in progress |

## Chat format

```
<|system|>
You are Hibari Koto, a friendly and calm AI companion. Keep replies short, kind and honest.<|eos|>
<|user|>
Hello!<|eos|>
<|assistant|>
Hello! What would you like to talk about?<|eos|>
```

Loss is computed on assistant tokens only.

## Not implemented

`training/fine_tune.py`, `hibari/configs/training/sft.yaml` (which
mentions LoRA) and `../../src/hibari/training/fine_tuning.py` are
placeholders. LoRA adapters (`checkpoints/adapters/`) are a roadmap item.
