# 16 — Dataset Catalog

Hibari Koto is trained on **7 public conversation datasets**, **3
public writing-help datasets** (from v5 on) and **two hand-written sets**
in the repository. Licences are from each dataset's Hugging Face metadata,
checked 2026-11-21. Check them again before redistributing data or a
model.

## Conversation data

| Dataset | Hugging Face ID | Licence (HF metadata) | Used (train / val) | Purpose |
|---|---|---|---|---|
| Empathetic Dialogues (LLM format) | `Estwld/empathetic_dialogues_llm` | apache-2.0 | 19,653 / 1,000 | emotional support |
| smol-smoltalk (3 subsets, first turn) | `HuggingFaceTB/smol-smoltalk` | apache-2.0 | 19,997 / 104 | short assistant answers, basic knowledge |
| Blended Skill Talk (personas removed) | `anezatra/blended-skill-talk` | apache-2.0 | 7,681 / 500 | open chit-chat |
| DailyDialog | `roskoN/dailydialog` | none in HF metadata (the original DailyDialog release is CC BY-NC-SA 4.0) | 7,543 / 500 | everyday dialogue |
| Everyday Conversations | `HuggingFaceTB/everyday-conversations-llama3.1-2k` | apache-2.0 | 3,120 ×2 / 163 | assistant-style small talk |
| ProsocialDialog | `allenai/prosocial-dialog` | cc-by-4.0 | 6,000 / 500 | replies to rude or unsafe input |
| OpenAssistant OASST1 (English, rank-0) | `OpenAssistant/oasst1` | apache-2.0 | 3,065 / 167 | general Q&A |

Counts are after cleaning, windowing, de-duplication and caps (base corpus
`data/processed/`, 71,715 train / 2,933 val). Fine-tune mixes sample
from this cache (`05_DATA_PIPELINE.md`).

## Writing-help data (v5 and later)

| Dataset | Hugging Face ID | Licence (HF metadata) | Used in v5 / v6 | What it teaches |
|---|---|---|---|---|
| CoEdIT (Grammarly, 2023) | `grammarly/coedit` | apache-2.0 | 12,000 / 20,000 | fix grammar (`gec`), paraphrase, simplify, clarify |
| ParaDetox | `s-nlp/paradetox` | openrail++ | 6,000 / 8,000 | rude → neutral rewrites |
| smol-rewrite (subset of SmolTalk) | `HuggingFaceTB/smoltalk` (`data/smol-rewrite`) | none in HF metadata | 2,299 / 2,299 | rewrite to professional / concise / friendly; mostly emails |

CoEdIT in detail: 69,071 rows (`gec` 19,823, `paraphrase` 15,370,
`simplification` 11,440, `coherence` 10,616, `neutralize` 10,570, `clarity`
1,252). Each `src` is `"<instruction>: <text>"`. Hibari uses gec,
paraphrase, simplification and clarity, and skips coherence (multi-sentence)
and neutralize. CoEdIT has no formality or politeness task; that gap is
filled by ParaDetox, smol-rewrite and the hand-written polite set.

smol-rewrite in detail: 53,342 rows across 3 system prompts (professional
21,139, concise 20,249, friendly 11,954). The style instruction is in the
system prompt, so Hibari turns it into a user request. Only about 7 % fit
the 256-token context.

### Considered and not used

| Dataset | Reason |
|---|---|
| `jhu-clsp/jfleg` | cc-by-nc-sa-4.0 (non-commercial) and only ~1.5k sentences |
| `liweili/c4_200m` | 200M synthetic grammar pairs, far too large for CPU training |
| GYAFC (formality) | not publicly downloadable (requires a Yahoo licence) |

## Hand-written data (in this repository)

| Module | Size | Content |
|---|---|---|
| `koto/data/curated.py` | 1,209 conversations | identity and creator, honesty about being a small AI, emotions, insults, harassment, being told to die, "I hate you", friend and family conflicts, "I already told you", hobbies / about you, crisis and violence replies, refusals, simple facts, multi-turn chains |
| `koto/data/conversation.py` | 2,460 train examples in 1.1.0 | small talk, 37 explained topics, fun facts, career advice, 3-turn context chains |
| `koto/data/dialogue_skills.py` | 1,677 unique (3,354 train examples ×2) | context recall, clarification questions, honest "I don't know", chat vs. correction, multiple / repeated questions |
| `koto/data/tasks.py` | hand-written rewriting sets | grammar, rephrase, formal / casual / shorter / simpler, meaning preservation |
| `koto/data/rewrite.py` (`build_polite_conversations`) | 1,160 conversations | 40 informal → polite pairs, 5 templated leave / sick / late families, 8 email topics × 6 recipients |

## Combined

| Mix | Train examples | Share of writing help | Share of curated |
|---|---|---|---|
| v2 base (`processed`) | 71,715 | 0 % | 2 % |
| v4 (`processed_full`) | 73,428 | 0 % | 4.4 % |
| v5 (`processed_v5`) | 57,455 | 39 % | 8.4 % |
| v6 (`processed_full_v6`) | 107,634 | 30 % | 4.5 % |
| 1.1.0 (`processed_1.1.0`) | 108,850 | 26.5 % | 3.3 % (+3.1 % dialogue skills) |

Loss is computed on assistant tokens only (system and user tokens are
`-100`). Special tokens: `<|system|>`, `<|user|>`, `<|assistant|>`,
`<|eos|>`, `<|pad|>`, `<|bos|>`, `<|unk|>`.

*See [05_DATA_PIPELINE.md](05_DATA_PIPELINE.md) for how the data is
processed and mixed.*
