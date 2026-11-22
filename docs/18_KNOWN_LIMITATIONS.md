# 18 — Known Limitations (Hibari Koto)

Measured results are in `09_EVALUATION_AND_TESTING.md` and in the
`outputs/metrics/eval_*.md` reports. This page explains what the
numbers mean in practice.

## Koto 1.1.0 (measured 2026-11-22)

Details and transcripts: `19_KOTO_1.1.0_DEVELOPMENT_REPORT.md`.

* **Open conversation got slightly worse.** Old-split validation perplexity
  20.86 (1.0.0) → 22.39 (1.1.0), worse on every general source. The same 6M
  parameters now also cover writing tasks.
* **Still invents facts.** "The capital of Japan is Berlin"; an invented
  weather forecast and a nonsense "prime minister" answer. The honest-limit
  data helps mainly for question types close to its templates (obscure
  figures, private facts), not for live data or general facts.
* **Context recall is partial.** Some facts are recalled ("You are in
  Coimbatore."), others come back wrong ("My name was Tancel." for Tanvir;
  the user's name instead of their subject).
* **Empathy and feedback are unreliable.** "I failed my driving test … I feel
  useless" → "I am sure you did well on it."
* **Writing tasks:** grammar correction passed 5 / 5 suite cases, but a
  fresh, more broken sentence ("i am not understand what you trying to say")
  was not corrected; formal rewrites pass 1 / 4.
* **More variation between seeds** than 1.0.0 (routed pass agreement 0.96 → 0.85).

## Model capacity

* **6.16 M parameters, trained from scratch on about 5 M supervised tokens
  per epoch.** That's roughly 20–200× smaller than small open chat models
  (135M–1.5B parameters). It produces short, mostly grammatical replies with
  the right tone for common conversational situations, but it doesn't
  reliably reason, follow complex instructions or recall facts.
  Knowledge-question relevance was 0 % for every version so far. Treat any
  factual answer as unverified. Training longer helps fluency (v4) but
  doesn't remove this ceiling; a much larger model would.
* **Intent mix-ups.** The model sometimes picks a reply learned for a
  different situation. Seen in tests: "That's great news!" for "i got fight
  with my friend", and its name given in answer to "what wrong with u?".
  Each mix-up has been addressed with more curated examples, but new
  phrasings can still trigger one.
* **Invented personas.** Human–human training dialogues (DailyDialog, Blended
  Skill Talk, Empathetic Dialogues, smoltalk role-play) can produce
  first-person claims ("My name is Jack Harris… working here for over 10
  years"). The `about_you` curated intent (v5) targets this.
* **Context: 256 tokens** (about 150–200 English words including the system
  prompt), about 5–6 short turns. Older turns are dropped by Ollama, cause an
  error in llama-server, and are trimmed at turn boundaries by the Python
  chat session.
* **System prompt.** Every training example used one fixed system prompt.
  Other system prompts or personas aren't reliably followed.
* **English only.** Other languages are tokenised (byte-level BPE) but not
  understood.

## Writing help (v5 and later)

* Works best on **one short sentence or message** similar to the training
  data: grammar fixes, polite rewrites, leave / sick / late messages, and
  short template emails.
* Longer text often comes back partly copied, partly changed or cut off.
  Only 2,299 of 53k smol-rewrite emails fit the context, so long-email
  rewriting is barely trained.
* Emails use fixed templates (`Subject:`, `Dear …`, `[Your name]`); fill in
  names and details yourself.
* Always read the output before sending it. A 6M model can change meaning,
  drop details or introduce new errors.
* Ollama's `num_predict 96` can cut long replies; raise it for emails.

## Safety

* The **deterministic safety layer exists only in the Python chat session**.
  It is pattern-based: it normalises slang and excludes common idioms, but it
  can't catch every phrasing (it doesn't understand context, sarcasm,
  third-person reports, or other languages).
* In **llama.cpp / Ollama / LM Studio / llama-cpp-python** there is no safety
  layer; only behaviour learned from curated self-harm / violence /
  refusal / hostility examples applies. Don't deploy the GGUF to vulnerable
  users without an external moderation layer.
* Crisis resources are India-focused (Tele-MANAS 14416, iCall, 112) with a
  generic "local emergency number" fallback.
* This is not a mental-health tool and must not be presented as one.

## Runtime

* Tokenisation in llama.cpp differs from Python only for Unicode
  compatibility characters (llama.cpp doesn't apply NFKC).
* For v4, all four GGUF formats (F32, F16, Q8_0, Q4_K_M) gave greedy replies
  identical to PyTorch on the 6 parity prompts. Q4_K_M can still diverge on
  other prompts; Q8_0 is the recommended size / quality balance and F32 is
  exact.
* The local llama.cpp binaries (`~/llama.cpp`) need
  `LD_LIBRARY_PATH="$LLAMA_CPP_HOME"` to find their shared libraries.
  `llama-completion` must be run with `-no-cnv`.
* LM Studio was not tested; it uses llama.cpp, so it is expected but **not
  verified** to work. The llama-server web UI was not tested (its API was).

## Evaluation

* All quality metrics are automated. "Relevance" and "grammar" are
  regex / surface heuristics, not human ratings; no systematic human
  evaluation was done. The Ollama conversation-replay counts in
  `09_EVALUATION_AND_TESTING.md` are hand-judged and approximate.
* The held-out suite has 58 cases (50 before 2026-11-21). Per-category
  percentages move in large steps (3–9 cases per category).
* Three eval safety prompts revealed gaps in the safety patterns during
  development, and the patterns were extended, so safety-layer recall on
  those prompts is optimistic.
* Some reported user prompts were later added to the curated training data
  in reworded form (identity, hostility, friend conflict). Improvements on
  those exact conversations therefore overstate generalisation. The
  held-out suite and the "unseen phrasings" set are the fairer measure.
