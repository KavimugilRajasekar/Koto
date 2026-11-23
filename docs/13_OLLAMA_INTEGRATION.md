# 13 — Ollama Integration

Hibari Koto GGUF files run in Ollama. Verified with **Ollama 0.40.1** on
Linux (CPU), which serves the model through its bundled llama.cpp runner.

> GGUF files made by the original (pre-v2) exporter must not be used: the F16
> file crashes llama.cpp-based runtimes and both files tokenize text
> differently from training. Re-export with `../../scripts/engine/export.py`.

## Install and run

The Modelfile must sit next to the GGUF it names in `FROM`.

```bash
cd releases/exported           # holds the exported GGUFs + a Modelfile (FROM ./Hibari-Koto-F32.gguf)
ollama create hibari-koto:6m-v4-f32 -f Modelfile
ollama run hibari-koto:6m-v4-f32
```

`releases/Modelfile` is the template: copy it next to a GGUF and edit its
`FROM` line to the F32, F16, Q8_0 or Q4_K_M file. If `ollama run` says
`could not connect to ollama server`, start it with `ollama serve`.

Inside `ollama run`: `/clear` resets the conversation, and
`/set parameter temperature 0` gives deterministic replies.

API example:

```bash
curl -s localhost:11434/api/chat -d '{
  "model": "hibari-koto:6m-v4-f32", "stream": false,
  "messages": [{"role": "user", "content": "Hi! How are you?"}]
}'
```

## Local model tags (2026-11-21)

| Tag | Built from | GGUF | Notes |
|---|---|---|---|
| `hibari-koto:6m` | v2 `best_model.pt` (step 3000) | F32 | original; weak on identity and insults |
| `hibari-koto:6m-v3` | v3 `best_model.pt` (step 2000) | F32 | best at identity and insults so far |
| `hibari-koto:6m-v4` | v4 `best_model.pt` (step 11000) | Q8_0 | most fluent |
| `hibari-koto:6m-v4-f32` | v4 `best_model.pt` (step 11000) | F32 | same weights, full precision |

Conversation-replay results for these tags are in
`09_EVALUATION_AND_TESTING.md`. Ollama names its stored files by the SHA-256
of their contents (`~/.ollama/models/blobs/sha256-…`), so deleting an
exported GGUF does not break a model that was already created from it.

## Modelfile

```dockerfile
FROM ./Hibari-Koto-F32.gguf

TEMPLATE """{{- if .System }}<|system|>
{{ .System }}<|eos|>
{{ end }}
{{- range .Messages }}
{{- if eq .Role "user" }}<|user|>
{{ .Content }}<|eos|>
{{ else if eq .Role "assistant" }}<|assistant|>
{{ .Content }}<|eos|>
{{ end }}
{{- end }}<|assistant|>
"""

SYSTEM """You are Hibari Koto, a friendly and calm AI companion. Keep replies short, kind and honest."""

PARAMETER stop "<|eos|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|system|>"
PARAMETER stop "<|assistant|>"
PARAMETER temperature 0.5
PARAMETER top_k 25
PARAMETER top_p 0.85
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 256
PARAMETER num_predict 96
```

* The template iterates `.Messages`, so multi-turn history is formatted
  exactly like the training data.
* The `SYSTEM` text is the one used for every training example; other system
  prompts are not reliably followed by a 6M-parameter model.
* `num_ctx 256` is the trained context length. When a conversation grows
  past it (about 5–6 turns), Ollama silently drops the oldest turns, and
  replies can then lose track. llama-server rejects such requests instead
  (`12_MODEL_EXPORT_AND_QUANTIZATION.md`).
* `num_predict 96` limits reply length. Writing-help replies (v5 and later,
  e.g. emails) can be longer; raise it with
  `/set parameter num_predict 160` if replies are cut off.

## What Ollama does NOT include

The Python chat session (`../../scripts/engine/generate.py`) adds a deterministic
safety layer for self-harm, violent intent and harmful-instruction requests.
**That layer does not exist in Ollama / llama.cpp.** There, only the
behaviour learned from the curated training examples applies, which is
weaker. Put an external moderation layer in front of any deployment that
real users can reach.
