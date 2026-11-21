# 19 — End-to-End Implementation of Hibari Koto

> **Historical.** This page records how the original **Hibari Koto 1M**
> baseline was built (1,024 vocab, 4 layers, `configs/*/koto_1m.yaml`). For
> the current Koto model see `05_DATA_PIPELINE.md`,
> `07_TRAINING_PIPELINE.md`, `09_EVALUATION_AND_TESTING.md` and
> `17_MODEL_CARD.md`.

## 1. Project Vision and Target Definition

The objective was to construct a functional, tiny text-based Large Language Model (LLM) named **Hibari Koto** (`Hibari-Koto-1M`) completely from scratch. 

Key constraints and specifications:
- **Parameter Target**: Approximately 1.0 Million parameters (actual: 984,192 parameters).
- **Domain**: Friendly, empathetic multi-turn conversational dialogue.
- **Data Source**: `anezatra/blended-skill-talk` from Hugging Face Datasets.
- **Export Target**: GGUF format (FP32 and FP16) for lightweight local inference via `llama.cpp` and `Ollama`.
- **Hardware Environment**: Standard CPU execution with PyTorch 2.10+ without GPU acceleration dependencies.

---

## 2. Environment and Dependency Engineering

### 2.1 Virtual Environment Setup
A isolated Python virtual environment was initialized at `.venv` with Python 3.14.

Core dependencies:
- `torch==2.10.0+cpu`: Lightweight CPU-only binary wheel avoiding heavy CUDA shared library overhead.
- `datasets==5.2.0`: For downloading and streaming Hugging Face datasets.
- `tokenizers==0.23.3`: High-performance Rust-backed BPE tokenizer training.
- `gguf==0.19.0`: Serialization library for writing GGUF binary models.
- `pytest==9.2.0`: Test runner for unit and integration testing.
- `pyyaml`, `tqdm`, `numpy`: Utility and numeric support.

### 2.2 Hugging Face Datasets Schema Patch
The target dataset `anezatra/blended-skill-talk` contains an issue in its YAML feature definition where `label_candidates: null` is parsed as `NoneType`. In `datasets==5.2.0`, `features.py`'s `from_yaml_inner` raised a `TypeError: Expected a dict or a list but got NoneType: None`.

To resolve this issue deterministically, `.venv/lib/python3.14/site-packages/datasets/features/features.py` was patched to return a default string value (`{"_type": "Value", "dtype": "string"}`) whenever a feature node is `None`. This allowed uninterrupted downloading and loading of all 4,096 training sequences.

---

## 3. Model Architecture from Mathematical First Principles

All architecture components were implemented without using pre-packaged model layers from external high-level libraries.

### 3.1 Model Hyperparameters
The configuration in `hibari/configs/model/koto_1m.yaml` sets:
- Vocabulary Size: `1,024` tokens
- Context Length: `256` tokens
- Hidden Dimension (`d_model`): `128`
- Number of Layers: `4`
- Number of Attention Heads: `4` (Head Dimension: `32`)
- FFN Hidden Dimension (`d_ff`): `384`
- Normalization Epsilon: `1e-5`
- Rotary Embeddings Base (`rope_theta`): `10000.0`
- Weight Tying: Enabled (`token_embeddings.weight == lm_head.weight`)
- Total Trainable Parameters: **984,192**

### 3.2 RMSNorm (Root Mean Square Normalization)
Implemented in `hibari/src/hibari/model/normalization.py`.
Unlike standard LayerNorm, RMSNorm does not calculate the mean of activations, saving compute while ensuring scale invariance:
$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d} \sum_{i=1}^d x_i^2 + \epsilon}} \odot \gamma$$

### 3.3 Rotary Position Embeddings (RoPE)
Implemented in `hibari/src/hibari/model/embedding.py`.
Frequencies are precomputed using:
$$\theta_i = 10000^{-2(i-1)/d}$$
RoPE rotates pairs of query and key vector dimensions by position angles, naturally incorporating relative token distances into the self-attention dot product without learned position tables.

### 3.4 Multi-Head Causal Self-Attention
Implemented in `hibari/src/hibari/model/attention.py`.
- Queries, keys, and values are projected from `d_model` (128) into 4 heads of dimension 32.
- RoPE rotations are applied to query and key states.
- An upper-triangular causal attention mask filled with $-\infty$ is applied before Softmax to prevent tokens from attending to future positions:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}} + M_{\text{causal}}\right) V$$
- Attention outputs are concatenated and projected back through an output projection layer.

### 3.5 SwiGLU Feed-Forward Network
Implemented in `hibari/src/hibari/model/transformer.py`.
SwiGLU replaces traditional two-layer MLPs with gated linear units:
$$\text{SwiGLU}(x) = (x W_{\text{gate}} \cdot \text{SiLU}(x W_{\text{up}})) W_{\text{down}}$$
Where $W_{\text{gate}}, W_{\text{up}} \in \mathbb{R}^{128 \times 384}$ and $W_{\text{down}} \in \mathbb{R}^{384 \times 128}$.

### 3.6 Transformer Block and Full LM
Each block combines Pre-RMSNorm, Causal Attention, residual addition, Pre-RMSNorm, SwiGLU FFN, and residual addition.
The complete language model (`HibariKotoLM` in `hibari/src/hibari/model/llm.py`) ties input token embeddings with the output linear head, keeping parameter count below 1.0M.

---

## 4. Tokenizer and Data Pipeline

### 4.1 Custom Byte-Level BPE Tokenizer
Implemented in `hibari/src/hibari/data/tokenizer.py`.
- Vocabulary size was constrained to 1,024 tokens to keep the embedding table lightweight (1,024 x 128 = 131,072 parameters).
- Byte-level byte-pair encoding ensures 100% fallback coverage for arbitrary UTF-8 characters without generating unknown token errors.
- Trained on 62,257 utterances extracted directly from `anezatra/blended-skill-talk`.
- Special tokens: `<|pad|>`, `<|unk|>`, `<|bos|>`, `<|eos|>`, `<|system|>`, `<|user|>`, `<|assistant|>`.
- Serialized to `hibari/models/tokenizer/tokenizer.json` and `tokenizer_config.json`.

### 4.2 Conversation Formatting
Implemented in `hibari/src/hibari/data/formatting.py`.
Raw records containing `free_messages` and `guided_messages` are transformed into turn-based chat templates:
```
<|system|>You are Hibari Koto, a friendly AI assistant.<|user|>Hello!<|assistant|>Hi! Great to chat with you.<|eos|>
```

### 4.3 Dataset and Batch Collator
Implemented in `hibari/src/hibari/data/dataset.py` and `collator.py`.
- Sequences are tokenized and truncated to `max_seq_len = 256`.
- Labels are aligned to `input_ids`.
- Padding positions are assigned label `-100` so that PyTorch's cross-entropy loss ignores padding tokens during loss computation.

---

## 5. Training Pipeline

### 5.1 Training Engine
Implemented in `hibari/src/hibari/training/trainer.py` and `scripts/train.py`.
- **Optimizer**: AdamW with weight decay `0.01`, $\beta_1 = 0.9, \beta_2 = 0.95$.
- **Learning Rate**: Peak learning rate $5 \times 10^{-4}$ with a 20-step linear warmup followed by cosine annealing decay.
- **Gradient Clipping**: Norm clipped at `1.0` to prevent gradient explosion.
- **Loss Function**: Cross-Entropy over shifted next-token predictions:
$$\mathcal{L} = -\frac{1}{T} \sum_{t=1}^{T} \log P(x_{t+1} \mid x_1, \dots, x_t)$$
- **Checkpoints**: Stored in `hibari/models/checkpoints/` (`best_model.pt`, step checkpoints, `final_model.pt`).

### 5.2 Training Run Metrics
- Dataset split: 4,096 train dialogues, 723 validation dialogues.
- Total training duration: 300 steps.
- Final Validation Loss: **3.5354**
- Final Validation Perplexity: **34.31**

---

## 6. Autoregressive Inference and Generation Engine

Implemented in `hibari/src/hibari/inference/engine.py`, `generation.py`, `sampling.py`, and `conversation.py`.

### 6.1 Generation Mechanics
1. Input text is tokenized into token IDs.
2. The model produces logits for the final sequence position.
3. Sampling is performed:
   - **Greedy**: $\arg\max_v z_v$
   - **Temperature**: Scaling logits by $1/T$ before softmax.
   - **Top-K**: Filtering to the $K$ highest probability tokens.
   - **Top-P (Nucleus)**: Filtering to the smallest subset of tokens with cumulative probability $\ge p$.
4. The selected token is appended to the context.
5. The process repeats until `<|eos|>` is emitted or `max_new_tokens` is reached.

### 6.2 Stateful Chat Session
`HibariChatSession` maintains the dialogue history, automatically formatting prior conversation turns with the appropriate role tags so multi-turn interactions retain context.

---

## 7. Native GGUF Binary Serialization

Implemented in `hibari/src/hibari/export/gguf_export.py` and `scripts/export.py`.

### 7.1 Architecture Mapping
To achieve full compatibility with `llama.cpp` and Ollama, the internal PyTorch weights were mapped to standard GGUF tensor naming conventions:
- `token_embeddings.weight` $\rightarrow$ `token_embd.weight`
- `layers.{i}.attention.q_proj.weight` $\rightarrow$ `blk.{i}.attn_q.weight`
- `layers.{i}.attention.k_proj.weight` $\rightarrow$ `blk.{i}.attn_k.weight`
- `layers.{i}.attention.v_proj.weight` $\rightarrow$ `blk.{i}.attn_v.weight`
- `layers.{i}.attention.out_proj.weight` $\rightarrow$ `blk.{i}.attn_output.weight`
- `layers.{i}.ffn.w_gate.weight` $\rightarrow$ `blk.{i}.ffn_gate.weight`
- `layers.{i}.ffn.w_up.weight` $\rightarrow$ `blk.{i}.ffn_up.weight`
- `layers.{i}.ffn.w_down.weight` $\rightarrow$ `blk.{i}.ffn_down.weight`
- `layers.{i}.norm1.weight` $\rightarrow$ `blk.{i}.attn_norm.weight`
- `layers.{i}.norm2.weight` $\rightarrow$ `blk.{i}.ffn_norm.weight`
- `final_norm.weight` $\rightarrow$ `output_norm.weight`
- `lm_head.weight` $\rightarrow$ `output.weight`

### 7.2 Exported Artifacts
- **FP32 Binary**: `hibari/models/exported/Hibari-Koto-1M.gguf` (File size: **4.27 MB**)
- **FP16 Binary**: `hibari/models/exported/Hibari-Koto-1M-f16.gguf` (File size: **2.14 MB**)

---

## 8. Verification and Quality Assurance

### 8.1 Automated Test Suite
All 13 automated tests in `hibari/tests/` passed:
- `test_model.py`: Configuration integrity, parameter count validation, forward pass output shapes, autoregressive generation loop.
- `test_tokenizer.py`: BPE training, encoding/decoding round-trip, chat template formatting.
- `test_dataset.py`: Raw dataset formatting and batch collator tensor padding.
- `test_inference.py`: Greedy sampling, temperature sampling, multi-turn `HibariChatSession`.
- `test_export.py`: GGUF serialization and header verification.
- `test_training.py`: Optimizer and trainer initialization.

### 8.2 End-to-End Chat CLI Test
The model was tested using `hibari/scripts/generate.py`:
```bash
python hibari/scripts/generate.py --prompt "Hi Koto! What do you enjoy doing?"
```
Output verified the conversational generation loop functions without error.

---

## 9. Version 2.0: Multi-Dataset Empathy & Coherence Upgrade

Following the baseline prototype, Hibari Koto was upgraded to Version 2.0 to eliminate sub-word token fragmentation and dramatically elevate conversational empathy:
- **Corpus Expansion**: Scaled from 1 dataset to 4 distinct dialogue datasets (`blended-skill-talk`, `dailydialog`, `prosocial-dialog`, `oasst1`), totaling 40,214 curated multi-turn conversations.
- **Tokenizer Expansion**: Re-trained Byte-Level BPE from 1,024 to 4,096 tokens, ensuring full English words and contractions tokenize cleanly without fragmentation.
- **Capacity Scale**: Expanded from ~1M parameters (4 layers, d_model=128) to ~6.16M parameters (6 layers, 8 heads, d_model=256, d_ff=768).
- **SFT Loss Masking**: Integrated prompt masking (`targets = -100` on system and user turns) so all gradient updates are focused purely on the assistant's empathetic response generation.

---

## 10. Conclusion

Hibari Koto demonstrates that a complete, modern decoder-only language model architecture can be designed, trained, evaluated, and packaged into standard deployment binaries (GGUF) using only CPU resources and first-principles PyTorch implementations.
