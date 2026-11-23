![Hibari](https://kavimugilrajasekar.github.io/assets/images/hibari/hibari-logo.jpeg)

# Hibari-Koto1.3.1:29M

**Koto 1.3.1** — a 29.4M-parameter conversational model trained from scratch on **Hibari**, an LLM
engine written from first principles in PyTorch by Kavimugil Rajasekar.

A small, friendly chat model for short conversations, empathy and simple writing help.

```
ollama run kavimugil-r/Hibari-Koto1.3.1:29M
```

## Model

| | |
|---|---|
| Parameters | 29,368,832 |
| Architecture | decoder-only Transformer (LLaMA-style): 8 blocks, d_model 512, 8 heads, SwiGLU 1536, RoPE, RMSNorm, tied embeddings |
| Context | 256 tokens |
| Vocabulary | 4,096 byte-level BPE tokens |
| Weights in this tag | Q8_0 GGUF (29.9 MiB), identical greedy output to the PyTorch model on 11/11 test prompts |
| Training | 93,509 conversations, 12,000 steps on one GPU (1.72 h), best validation loss 2.781 |

## Architecture

![Hibari Koto overall architecture](https://kavimugilrajasekar.github.io/assets/images/hibari/hibari-koto-overall-architecture.jpeg)

Chat turns → byte-level BPE tokenizer → embedding → 8 pre-norm Transformer blocks → RMSNorm → tied LM head → sampling.

![Transformer block](https://kavimugilrajasekar.github.io/assets/images/hibari/hibari-koto-transformer-block.jpeg)

![Multi-head causal attention with RoPE and KV cache](https://kavimugilrajasekar.github.io/assets/images/hibari/hibari-koto-attention.jpeg)

![Token embedding and tied output projection](https://kavimugilrajasekar.github.io/assets/images/hibari/hibari-koto-embedding-and-output.jpeg)

The diagrams show the 29.4M architecture shared by Koto 1.3.0 and 1.3.1; 1.3.1 adds residual dropout 0.1 in training.
Full walkthrough: https://kavimugilrajasekar.github.io/hibari/architecture.html

## Results (Python release pipeline, seeds 0 1 2)

| Suite | Koto 1.1.1 | **Koto 1.3.1** |
|---|---|---|
| Behaviour suite (52 cases) | 0.660 | **0.628** |
| Conversation suite (15 cases) | 0.645 | **0.733** |

Better than 1.1.1 at multi-turn context, robustness and safety; **weaker at rewriting** (rephrase,
make formal) and e-mail writing.

## Notes

- Ollama runs the raw model: the Hibari Python engine's safety layer, rewriting router and reply
  reranking are not included. It is not a crisis service.
- It invents facts and has a short memory (256 tokens). English only.
- Licence: MIT. Part of the training data is non-commercial (DailyDialog, CC BY-NC-SA 4.0) and part
  OpenRAIL++ (ParaDetox); check those terms before commercial use.

## Links

- Hugging Face (all GGUFs, PyTorch checkpoint, model card): https://huggingface.co/kavimugil-r/Hibari-Koto
- Hibari engine: https://github.com/KavimugilRajasekar/Hibari
- Koto model: https://github.com/KavimugilRajasekar/Koto
- Project page: https://kavimugilrajasekar.github.io/hibari/index.html
- Author: https://huggingface.co/kavimugil-r · https://github.com/KavimugilRajasekar
