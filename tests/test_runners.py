"""Koto runners that the suite did not reach before (2026-11-23 coverage pass):
the behaviour-evaluation runner (pipelines, a full case through the chat session, summary,
markdown) and the remaining branches of training/train.py."""

import json

import pytest
import torch
import yaml

from hibari.model.config import ModelConfig
from hibari.model.llm import HibariKotoLM
from hibari.release import ModelProfile
from koto import KOTO_ROOT
from koto.paths import TOKENIZER_DIR

import evaluation.evaluate_behaviour as eb
from hibari.data.tokenizer import HibariTokenizer


@pytest.fixture(scope="module")
def profile():
    return ModelProfile.load(KOTO_ROOT / "configs/release/koto_1.1.1.yaml")


@pytest.fixture(scope="module")
def tiny():
    tok = HibariTokenizer.load(TOKENIZER_DIR)
    torch.manual_seed(0)
    cfg = ModelConfig(vocab_size=tok.vocab_size, max_seq_len=256, d_model=32, n_layers=1, n_heads=2, d_ff=64)
    return HibariKotoLM(cfg).eval(), tok


def test_pipelines_differ_only_in_the_documented_switches(profile):
    raw, base, rel = (eb.pipeline_kwargs(n, profile) for n in ("raw", "baseline", "release"))
    assert raw["enable_safety"] is False and raw["num_candidates"] == 1 and not raw["route_tasks"]
    assert base["enable_safety"] is True and base["route_tasks"] is True and base["num_candidates"] == 1
    assert rel["num_candidates"] == profile.inference.num_candidates >= 1
    assert raw["system_prompt"] == rel["system_prompt"] == profile.system_prompt
    with pytest.raises(KeyError):
        eb.pipeline_kwargs("nope", profile)


def test_a_multi_turn_case_runs_through_the_release_pipeline_and_is_scored(profile, tiny):
    model, tok = tiny
    case = next(c for c in eb.CASES if len(c.turns) > 1)
    kw = dict(eb.pipeline_kwargs("release", profile), num_candidates=2)
    rows = eb.run_case_torch(model, tok, case, kw, dict(max_new_tokens=8), seed=0)
    assert [r["turn"] for r in rows] == list(range(len(case.turns)))
    scored = [r for r in rows if r.get("scored")]
    assert scored and all("checks" in r and "passed" in r for r in scored)
    assert all(isinstance(r["output"], str) for r in rows)


def test_run_summarise_and_markdown_cover_every_case(monkeypatch):
    def fake_runner(case):
        return [{"turn": i, "input": t, "output": "I'm an AI, I am a real person | yes", "seconds": 0.1,
                 "routed_task": None, "safety_category": "none",
                 **({"scored": True, "passed": i % 2 == 0, "checks": {"no_human_claim": False, "affect:x": True},
                     "failed_checks": ["no_human_claim"]} if i in case.checks else {})}
                for i, t in enumerate(case.turns)]
    res = eb.run("release/seed0", fake_runner)
    s = res["summary"]
    assert s["cases"] == len(eb.CASES) and 0 <= s["pass_rate"] <= 1
    assert s["metrics"]["no_human_claim"] == 0.0 and s["metrics"]["affect_checks"] == 1.0
    assert set(s["by_category"]) <= set(eb.CATEGORY_ORDER)
    rep = {"name": "t", "profile": "p", "model_version": "x", "weights_version": "y", "checkpoint": "c",
           "generated": "now", "machine": "m", "reply_settings": {}, "runs": {"release/seed0": res, "release/seed1": res},
           "stability": {"release": {"agreement": 1.0, "pass_rates": [s["pass_rate"]] * 2}}}
    md = eb.to_markdown(rep)
    assert md.count("## Transcripts") == 1 and "\\|" in md and "Seed stability" in md
    assert eb.esc("x" * 400).endswith("…") and len(eb.esc("x" * 400)) == 260


# ───────────── training/train.py branches ─────────────

def _setup(tmp_path, **extra):
    from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
    data = tmp_path / "data"
    data.mkdir()
    conv = {"source": "t", "messages": [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                                         {"role": "user", "content": "hello"}, {"role": "assistant", "content": "Hi there!"}]}
    (data / "train_conversations.json").write_text(json.dumps([conv] * 8))
    (data / "val_conversations.json").write_text(json.dumps([conv] * 2))
    m = tmp_path / "model.yaml"
    m.write_text(yaml.safe_dump({"model_name": "tiny", "vocab_size": 4096, "max_seq_len": 64, "d_model": 32,
                                 "n_layers": 1, "n_heads": 2, "d_ff": 64}))
    t = tmp_path / "train.yaml"
    t.write_text(yaml.safe_dump({"data_cache_dir": str(data), "max_steps": 2, "batch_size": 4, "warmup_steps": 1,
                                 "eval_every": 2, "checkpoint_every": 2, "log_every": 1, "output_dir": str(tmp_path / "out"),
                                 "val_examples": 2, **extra}))
    return str(m), str(t)


def test_unknown_fingerprint_key_is_refused(tmp_path):
    from training.train import train
    m, t = _setup(tmp_path, data_fingerprint={"train_examples": 8})
    with pytest.raises(SystemExit, match="unknown keys"):
        train(model_config_path=m, training_config_path=t, tokenizer_dir=str(TOKENIZER_DIR))


def test_missing_processed_data_is_reported(tmp_path):
    from training.train import train
    m, t = _setup(tmp_path)
    (tmp_path / "data" / "train_conversations.json").unlink()
    with pytest.raises(FileNotFoundError, match="Build the data first"):
        train(model_config_path=m, training_config_path=t, tokenizer_dir=str(TOKENIZER_DIR))


def test_fine_tune_from_init_checkpoint_with_max_steps_override(tmp_path):
    from training.train import train
    m, t = _setup(tmp_path)
    train(model_config_path=m, training_config_path=t, tokenizer_dir=str(TOKENIZER_DIR))
    first = tmp_path / "out" / "best_model.pt"
    (tmp_path / "ft").mkdir()
    m2, t2 = _setup(tmp_path / "ft", init_checkpoint=str(first))
    train(model_config_path=m2, training_config_path=t2, tokenizer_dir=str(TOKENIZER_DIR), max_steps_override=1)
    meta = json.loads((tmp_path / "ft" / "out" / "training_history.json").read_text())
    assert meta["metadata"]["init_checkpoint"] and meta["best"]["final_step"] == 1
