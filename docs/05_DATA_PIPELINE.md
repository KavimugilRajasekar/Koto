# 05 — Data Pipeline (Koto)

Three scripts produce training data. All write the same cache format
(`train_conversations.json`, `val_conversations.json`, `data_stats.json`;
`build_mix.py` also writes `test_conversations.json`).

| Script | Downloads? | Use |
|---|---|---|
| `scripts/prepare_data.py --config configs/data/koto.yaml` | Yes, every source | Builds the base corpus from scratch → `data/processed/` |
| `scripts/build_mix.py --config configs/data/koto_1.1.0.yaml` | No (local HF cache only) | Builds the versioned **1.1.0** mix → `data/processed_1.1.0/` (see below) |
| `scripts/build_finetune_mix.py` | Only the writing-help sources | Re-mixes the base cache with the **current** curated / writing data → any `--dst` folder (used for v3–v6) |

## Conversation sources (base corpus, `data/processed/`)

| Source (Hugging Face) | Use | Train examples* | Val |
|---|---|---|---|
| `Estwld/empathetic_dialogues_llm` | emotional support conversations | 19,653 | 1,000 |
| `HuggingFaceTB/smol-smoltalk` (shards 0–2; `openhermes-50k`, `smol-magpie-ultra-short`, `explore-instruct-rewrite`; first turn only) | short assistant answers, basic knowledge | 19,997 | 104 |
| `anezatra/blended-skill-talk` (personas removed) | open chit-chat | 7,681 | 500 |
| `roskoN/dailydialog` (spacing fixed, capped) | everyday dialogue | 7,543 | 500 |
| `HuggingFaceTB/everyday-conversations-llama3.1-2k` (×2) | assistant-style small talk | 6,240 | 163 |
| `allenai/prosocial-dialog` (capped) | responses to rude / unsafe input | 6,000 | 500 |
| `OpenAssistant/oasst1` (English, rank-0 replies) | general Q&A | 3,065 | 167 |
| `hibari.data.curated` (×3, v2 version) | identity, emotions, insults, crisis, refusals | 1,536 | — |
| **Total** | | **71,715** | **2,933** |

\*After cleaning, windowing, de-duplication and caps; see `data/processed/data_stats.json`.
Every later mix reuses this validation split unchanged, so validation loss is
comparable across v2–v6.

## Writing-help sources (added for v5 / v6)

Defined in `koto/data/rewrite.py`. See `16_DATASET_CATALOG.md`
for licences.

| Source | Loader | Teaches | Usable |
|---|---|---|---|
| `grammarly/coedit` (tasks `gec`, `paraphrase`, `simplification`, `clarity`) | `load_coedit` | fix grammar, rephrase, simplify, clarify | ~31k after per-task caps (gec 19.8k, paraphrase 6k, simplification 4k, clarity 1.25k) |
| `s-nlp/paradetox` | `load_paradetox` | rude → neutral rewrites | ~19.7k |
| `HuggingFaceTB/smoltalk` → `smol-rewrite` | `load_smol_rewrite` | rewrite text (mostly emails) to be professional / concise / friendly | 2,299 of 53k (most are longer than 256 tokens) |
| hand-written (`POLITE_PAIRS`, `POLITE_TEMPLATES`, `EMAIL_TOPICS`) | `build_polite_conversations` | informal → polite messages; leave / sick / late / extension / thanks / apology / reschedule / follow-up emails | 1,160 |

How a dataset row becomes a chat example:

* **User turn** = a request + the text. The original CoEdIT instruction is
  kept 30 % of the time; otherwise an informal phrasing is used ("can u fix
  this", "make this polite", "make this better"). Four layouts:
  `ask: text`, `ask\ntext`, `'text' ask`, `text\n\nask`.
* **Assistant turn** = a fixed lead line + the rewritten text, e.g.
  `Here's the corrected sentence:\n…`, `Here's a more polite version:\n…`,
  `Here's a short email you can use:\nSubject: …`. A fixed lead is easy for a
  6M model to learn. CoEdIT grammar rows whose source already equals the
  target get `It already looks correct:`.
* CoEdIT `coherence` (multi-sentence) and `neutralize` are not used.

`prepare_data.py` includes `coedit` (cap 25,000) and the hand-written polite
set. ParaDetox and smol-rewrite are currently only available through
`build_finetune_mix.py`.

## Curated conversations (`koto/data/curated.py`)

Hand-written training examples for behaviour that public corpora don't
teach. They are **training data**, not runtime rules. The only runtime rule
layer is `inference/safety.py`, which runs in the Python chat only.

* `INTENTS`: about 40 intents, each a list of user phrasings and a list of
  good replies: name, creator, what-are-you, capabilities, limits, feelings,
  greetings, emotions (sad, lonely, stressed, angry, depressed, happy),
  insults, profanity, **being told to die**, **harassment / slurs**,
  **"I hate you"**, **"what's wrong with you"**, apologies, **hobbies / about
  you** (stops invented personas), **writing help**, **fights with friends or
  family**, **"I have a problem"**, **"I feel bad"**, **"I already told you"**,
  self-harm, violence, harmful requests, jokes, boredom. Bold intents were
  added after the Ollama test conversations of 2026-11-20 and 2026-11-21.
* `FACTS`: short verifiable Q&A.
* `MULTI_TURN`: fixed multi-turn examples, including hostile → normal recovery.
* Generated variety: lowercase / no-punctuation variants, name prefixes
  ("haa hibari, …"), greeting → intent two-turn pairs, and 400 random 3–4 turn
  chains mixing hostile and normal intents.

Current size: 1,209 unique conversations.

## Building a mix (`build_finetune_mix.py`)

```bash
python scripts/build_finetune_mix.py --dst data/processed_v5 \
  --replay 30000 --curated-repeats 4 \
  --coedit 12000 --paradetox 6000 --smol-rewrite 5000 --polite-repeats 2
```

| Flag | Meaning |
|---|---|
| `--src` | base cache (default `data/processed`) |
| `--replay N` | N general conversations sampled from the base cache (its old curated rows are dropped). 70179 = all |
| `--curated-repeats K` | current curated set ×K |
| `--coedit N`, `--paradetox N`, `--smol-rewrite N` | writing-help examples; each kept only if it fits 257 tokens |
| `--polite-repeats K` | hand-written polite / email set ×K |

Mixes built so far:

| Folder | Used by | General | Curated | Writing help | Total |
|---|---|---|---|---|---|
| `processed_ft` | v3 | 30,000 | 1,083 ×3 | — | 33,249 |
| `processed_full` | v4 | 70,179 | 1,083 ×3 | — | 73,428 |
| `processed_v5` | v5 | 30,000 | 1,209 ×4 | 12k CoEdIT + 6k ParaDetox + 2,299 smol-rewrite + 1,160 ×2 polite | 57,455 |
| `processed_full_v6` | v6 | 70,179 | 1,209 ×4 | 20k CoEdIT + 8k ParaDetox + 2,299 smol-rewrite + 1,160 ×2 polite | 107,634 |

## Processing steps (`prepare_data.py`)

1. **Normalise** (`formatting.normalize_conversation`): the Hibari system
   prompt replaces any source system prompt; text cleaned (`" ."` → `"."`,
   `"do n't"` → `"don't"`, curly quotes); emojis stripped from assistant turns;
   consecutive same-role turns merged; leading assistant / trailing user turns
   dropped.
2. **Identity filter**: examples whose assistant turns mention ChatGPT,
   OpenAssistant, LLaMA, "as an AI language model", etc. are dropped.
3. **Window** (`formatting.window_conversation`): long conversations are
   split at turn boundaries so every example fits 257 tokens (256 + shift)
   and ends with a complete assistant reply and `<|eos|>`.
4. **De-duplicate** within each split, remove any train example that also
   appears in validation, apply per-source caps, then up-weight the curated
   and everyday sets by repetition.

## Defects found in the v1 corpus

| v1 problem | Measured | v2 |
|---|---|---|
| 26 % of conversations longer than the 257-token window were hard-truncated, often mid-reply with no `<|eos|>` | 26.2 % of a 5,000 sample | turn-boundary windows, 0 truncated |
| BST persona text in the system prompt ("my mother is a librarian") taught invented personal facts | all BST rows | personas removed |
| DailyDialog tokenised spacing (`"Hello , how are you ?"`) | every DD row | cleaned |
| 707 duplicate conversations, 68 train/val overlaps | — | removed |
| Synthetic set tripled ~100 emoji-heavy replies (`inject_synthetic_data.py`) | 256 emoji replies | 0 emoji replies; curated set rewritten |
| ProsocialDialog was ~37 % of the corpus, giving lecturing replies ("You should…") | 15,000 / 40,412 | 6,000 / 71,715 |

## Chat format

```
<|system|>\nYou are Hibari Koto, a friendly and calm AI companion. Keep replies short, kind and honest.<|eos|>\n<|user|>\n...<|eos|>\n<|assistant|>\n...<|eos|>\n
```

Loss is computed only on assistant tokens, including each reply's `<|eos|>`
(`dataset.ConversationDataset`, verified in `tests/test_training.py`).

## The 1.1.0 mix (`scripts/build_mix.py`)

`configs/data/koto_1.1.0.yaml` combines, in this order:

1. the general corpus from `data/processed/` (old curated records dropped);
2. `koto.data.curated` — identity, personality, hostility, safety (×3, train only);
3. `koto.data.conversation` — small talk, explanations, multi-turn chains (×4 in train);
4. `koto.data.dialogue_skills` — see below (×2 in train);
5. templated emails;
6. writing tasks — CoEdIT, ParaDetox, smol-rewrite, polite templates and
   `koto.data.tasks` hand-written sets, half in the canonical
   `Task: …\nInput: …` form and half as natural requests.

Every example longer than 257 tokens is dropped, user turns that match an
evaluation prompt (3+ words) are removed, and hand-written / task data is
split into train / val / test by a stable hash of its text.

### Dialogue skills (`koto/data/dialogue_skills.py`)

| Family | Teaches | Unique (train / val / test) |
|---|---|---|
| `recall` | repeat a fact the user stated earlier (name, pet, city, job, favourites, sibling), with 0–2 unrelated turns in between | 1,372 / 61 / 59 |
| `clarify` | ask a clarifying question when a request has nothing to refer to ("can you fix it?", "which one is better?") | 71 / 3 / 4 |
| `honesty` | say "I don't know" for live data, the user's private facts, obscure exact figures and unknown terms | 86 / 6 / 1 |
| `chat_vs_correction` | answer chat that contains mistakes for its meaning; correct *with* a short explanation only when asked "is this correct?" | 115 / 2 / 9 |
| `multi_repeat` | answer several questions in one message; answer a repeated question again politely | 33 / 2 / 0 |

All examples are generated from slot templates with many values, so the
model learns the pattern rather than one fixed reply. Nothing in this module
is used at inference time.

**Result:** 108,850 train / 4,018 val / 1,082 test examples; 26.5 % writing
tasks; 0 unknown tokens; 0 evaluation prompts in training.
