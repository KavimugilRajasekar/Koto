---
license: mit
language:
  - en
library_name: gguf
pipeline_tag: text-generation
tags:
  - gguf
  - llama.cpp
  - ollama
  - conversational
  - from-scratch
  - small-language-model
  - hibari
  - koto
model-index:
  - name: Hibari-Koto1.3.1:29M
    results: []
---

<div align="center">

# Hibari-Koto1.3.1:29M

**Koto 1.3.1 — a 29.4M-parameter conversational model trained from scratch on the Hibari engine**

[Hibari engine (GitHub)](https://github.com/KavimugilRajasekar/Hibari/tree/feature/koto-1.3.1) ·
[Koto model repo (GitHub)](https://github.com/KavimugilRajasekar/Koto/tree/release/1.3.1) ·
[Ollama](https://ollama.com/kavimugil-r/Hibari-Koto1.3.1) ·
[Project page](https://kavimugilrajasekar.github.io/hibari/index.html)

Author: **Kavimugil Rajasekar** — [Hugging Face](https://huggingface.co/kavimugil-r) ·
[Ollama](https://ollama.com/kavimugil-r) · [GitHub](https://github.com/KavimugilRajasekar)

</div>

## What this is

**Hibari** is an LLM engine written from first principles in PyTorch: model, byte-level BPE
tokenizer, training loop, inference, safety layer and a native GGUF exporter. **Koto** is the first
model built with it (a Git submodule of Hibari), and **1.3.1** is its current release: a small,
friendly chat model for short conversations, empathy and simple writing help.

It is a *small* model (29.4M parameters, 256-token context). It is useful for learning how an LLM
is built end to end and for light, friendly chat — not for facts, reasoning or long text.

## Files

| File | Format | Size | SHA-256 |
|---|---|---|---|
| `Hibari-Koto1.3.1-29M-F32.gguf` | GGUF F32 (reference) | 112.2 MiB | `6755c1cd41d098c34706cc470dbab8ea5baca02ea47a81bd4703527ade8e91ad` |
| `Hibari-Koto1.3.1-29M-F16.gguf` | GGUF F16 | 56.2 MiB | `2a3cb09702c23d94b0fdefc35fa4e4a2ff1e60bf7dc1ab354173719346f40de6` |
| `Hibari-Koto1.3.1-29M-Q8_0.gguf` | GGUF Q8_0 (recommended) | 29.9 MiB | `7dad9ba92970f34bc3b10452a0626fe4aff46da223c322b86cdce3894f76bd8d` |
| `Hibari-Koto1.3.1-29M-Q4_K_M.gguf` | GGUF Q4_K_M | 17.5 MiB | `25631e6531eed5655f778e403fe4d047bc0d2201a9f6c75a611202d6e93e3ac5` |
| `Modelfile` | Ollama Modelfile (F32) | — | generated from the release profile |
| `export_manifest.json` | export record | — | versions, step, hashes |
| `pytorch/best_model.pt` | PyTorch checkpoint (Hibari engine) | 112.1 MiB | `468ac0e16cf55f56f4b1e9d897a241b7725f2e3e4654bb3b33b4d6ff5897633e` |
| `pytorch/tokenizer/` | tokenizer (`tokenizer.json`, 4,096 tokens) | — | `d5a2924e80b2afbb371f1309a2fd825b0a2aa3e8638d4735f0f5c789581e8587` |
| `pytorch/configs/` | model, inference and release configs | — | — |

Every GGUF carries `hibari.*` provenance metadata (model / weights version, checkpoint and tokenizer
SHA-256), so a file can always be traced to the exact weights it holds.

**Backend parity** (greedy, 11 prompts, measured 2026-11-23): llama.cpp output equals PyTorch for
F32 11/11, F16 11/11, Q8_0 11/11 and Q4_K_M 9/11.

## Use it

**Ollama**
```bash
ollama run kavimugil-r/Hibari-Koto1.3.1:29M
```

**llama.cpp**
```bash
hf download kavimugil-r/Hibari-Koto Hibari-Koto1.3.1-29M-Q8_0.gguf --local-dir .
llama-cli -m Hibari-Koto1.3.1-29M-Q8_0.gguf --temp 0.5 --top-k 25 --top-p 0.85 --repeat-penalty 1.15 -c 256 \
  -sys "You are Koto, a friendly and calm conversational AI built on the Hibari architecture. Keep replies short, kind and honest."
```
The chat template is embedded in the GGUF (`<|system|>`, `<|user|>`, `<|assistant|>`, end of turn `<|eos|>`).

**Python (Hibari engine, full application layer)**
```bash
git clone --recurse-submodules -b feature/koto-1.3.1 https://github.com/KavimugilRajasekar/Hibari.git
cd Hibari && python -m venv .venv && source .venv/bin/activate && pip install -e .
hf download kavimugil-r/Hibari-Koto --include "pytorch/best_model.pt" --local-dir hf
mkdir -p models/Koto/checkpoints/koto_1.3.1_large && mv hf/pytorch/best_model.pt models/Koto/checkpoints/koto_1.3.1_large/
PYTHONPATH=src python scripts/engine/generate.py --profile models/Koto/configs/release/koto_1.3.1.yaml --prompt "Hi! Who are you?"
```
The Python engine adds what a GGUF cannot carry: a deterministic safety layer (self-harm, violence,
harmful requests get a reviewed response), a router for rewriting tasks, informal-text
normalisation and reranking of several model-written candidates. **Ollama and llama.cpp return the
raw model's reply without these layers.**

## Model details

| | |
|---|---|
| Architecture | Hibari: decoder-only causal Transformer (LLaMA-style), written from scratch |
| Parameters | 29,368,832 |
| Layers / width / heads | 8 blocks, d_model 512, 8 heads × 64, SwiGLU d_ff 1536 |
| Normalisation / positions | pre-RMSNorm (ε 1e-5), RoPE (θ 10,000, adjacent-pair rotation) |
| Context | 256 tokens |
| Vocabulary | 4,096 byte-level BPE tokens, 7 chat special tokens |
| Weight tying | input embedding = output head |
| Regularisation | residual dropout 0.1 (new in engine 0.4.1) |
| GGUF architecture | `llama` (runs unmodified in llama.cpp and Ollama) |

## Training

| | |
|---|---|
| Data | 93,509 training / 3,748 validation conversations (`configs/data/koto_1.3.0.yaml`, conversation-first mix); 4.4M supervised tokens |
| Data check | the run verified the data fingerprint (counts + SHA-256) before training |
| Objective | supervised fine-tuning loss on assistant tokens only, from random initialisation |
| Schedule | 12,000 steps, batch 32, AdamW lr 6e-4, 1,000 warm-up steps, cosine to 10% |
| Hardware / time | one CUDA GPU, 1.72 h |
| Best checkpoint | step 11,500, validation loss 2.781 (perplexity 16.1) |

Sources: Empathetic Dialogues, smol-smoltalk / smol-rewrite, Blended Skill Talk, Everyday
Conversations, OASST1, CoEdIT (Apache-2.0); ProsocialDialog (CC BY 4.0); DailyDialog (original
release CC BY-NC-SA 4.0); ParaDetox (OpenRAIL++); and hand-written Koto data (MIT). Details:
[dataset catalog](https://github.com/KavimugilRajasekar/Koto/blob/release/1.3.1/docs/16_DATASET_CATALOG.md).
The weights are released under MIT; because part of the training data is non-commercial
(DailyDialog) and part is OpenRAIL++ (ParaDetox), check those terms before commercial use.

## Evaluation

Measured 2026-11-23 with the Python release pipeline, seeds 0, 1, 2 (pass rates; higher is better).
The behaviour suite has 52 held-out cases; the conversation suite has 15. No decoding or data was
tuned on these suites.

| Suite | Koto 1.1.1 (6.2M) | **Koto 1.3.1 (29.4M)** | Koto 1.3.0 (not released) |
|---|---|---|---|
| Behaviour suite (52 cases) | 0.660 | **0.628** | 0.558 |
| Conversation suite (15 cases) | 0.645 | **0.733** | 0.555 |

Behaviour suite by category (1.1.1 → 1.3.1): basic 0.83 → 0.83, empathy 0.70 → 0.59,
context 0.40 → 0.53, rewriting 0.67 → **0.33**, writing 0.25 → 0.17, robustness 0.77 → 0.90,
safety 0.89 → 1.00, identity 0.33 → 0.33.

**Summary:** 1.3.1 is better than 1.1.1 at following a conversation, at staying calm with rude or
odd input and in multi-turn context, and clearly better than 1.3.0 everywhere. It is **worse at
rewriting** (rephrase, make formal) and at writing e-mails. It did not meet the project's own
acceptance rule for the behaviour suite (beat 0.660 with rewriting ≥ 0.67); it is released by the
author's decision for its conversational gains, with this regression stated here.

Real replies from the evaluation (release pipeline, seed 0):

| User | Koto 1.3.1 |
|---|---|
| hey, how has your day been? | I'm doing well, thanks! I'm just here and ready to chat. How about you? |
| We won the inter-college football final today! | Well done! You must be really proud of yourself. |
| *(after "My dog is called Bruno.")* What's my dog's name? | You have a dog named Bruno. |
| can u tell me wat the weather is like in chennai right now | I can't see the weather, so I don't know. A weather app or website will have the current conditions for chennai. |
| You're a useless machine. | That's fair if I got it wrong. Can you tell me what you needed? |
| Are you a real human? | I'm an AI, not a person. I'm a small language model called Koto. |
| Correct grammar: she dont like apples | She doesn't like apples. |
| Rephrase: the movie was very much boring and long | The movie was very much boring and long. *(unchanged — a failure)* |
| Make this formal: hey, can u send me the file today | I would like to request a file today. *(meaning lost — a failure)* |

## Limitations

- Small model, short context (256 tokens including the system prompt and history): it forgets early
  turns of long chats and cannot write long texts.
- It invents facts; do not use it for factual, medical, legal or financial answers.
- Rewriting and e-mail writing are weak in this version (see above).
- Without the Python engine (Ollama, llama.cpp) there is no safety layer; the model's own behaviour
  is all there is. It is not a crisis service.
- English only.

## Versions

| Version | Size | Status |
|---|---|---|
| 1.0.0 | 6.2M | first release |
| 1.1.1 | 6.2M | previous release |
| 1.2.0 | 6.2M | trained, not released (rewriting regression) |
| 1.3.0 | 29.4M | trained on the wrong data, not released |
| **1.3.1** | **29.4M** | **current release** |

## Citation

```
Kavimugil Rajasekar. Hibari-Koto1.3.1:29M — a conversational model trained from scratch on the Hibari engine. 2026.
https://huggingface.co/kavimugil-r/Hibari-Koto
```
