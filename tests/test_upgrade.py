"""Tests for the Koto 1.1.0 data, evaluation suite and training entry point."""

import json
import random
import re

import pytest
import yaml
import koto

from hibari.evaluation.metrics import has_lead
from hibari.inference.tasks import TASKS, parse_task_request
from koto.data.conversation import (
    BUILD,
    LEARNING,
    PROBLEMS,
    all_conversation_user_texts,
    build_conversation_conversations,
)
from koto.data.rewrite import POLITE_PAIRS, polite_examples
from koto.data.tasks import (
    NATURAL_ASKS,
    TaskExample,
    dedup_examples,
    grammar_pairs,
    handwritten_task_examples,
    is_faithful,
    norm,
    remove_leaks,
    render,
    split_of,
)
from koto.evaluation.upgrade_suite import CASES, CATEGORY_ORDER, eval_user_texts, score_turn


def _eval_norms():
    return {norm(t) for t in eval_user_texts() if norm(t)}


# ───────────── task data ─────────────

def test_canonical_and_natural_requests_parse_back_to_the_same_task():
    """The request forms used in training are the ones the engine recognises."""
    rng = random.Random(0)
    for task, asks in NATURAL_ASKS.items():
        for ask in asks:
            for msg in (f'{ask}: "she go home"', f"{ask}: she go home", f"{ask}\nshe go home"):
                req = parse_task_request(msg)
                assert req is not None and req.task == task and req.text == "she go home", msg
    for ex in handwritten_task_examples()[:300]:
        user = render(ex, rng, canonical_share=1.0)[0]["content"]
        req = parse_task_request(user)
        assert req and req.task == ex.task and req.text == ex.source.strip()


def test_task_replies_are_the_rewritten_text_only():
    rng = random.Random(1)
    for ex in handwritten_task_examples() + polite_examples(n_templated=50):
        conv = render(ex, rng)
        assert conv[1]["content"] == ex.target
        assert not has_lead(ex.target), ex


def test_grammar_targets_are_well_formed_and_change_the_input():
    for wrong, right, pattern in grammar_pairs(random.Random(2), n_per_pattern=40):
        assert right[0].isupper() and right.endswith((".", "?")), right
        assert wrong != right, pattern
        assert "  " not in right


def test_dedup_counts_contradictions():
    exs = [TaskExample("rephrase", "a b", "A b.", "x"), TaskExample("rephrase", "A b!", "A b.", "x"),
           TaskExample("rephrase", "a b", "Different.", "x"), TaskExample("formal", "a b", "Different.", "x")]
    out, stats = dedup_examples(exs)
    assert len(out) == 2 and stats == {"duplicate": 1, "contradiction": 1}


def test_split_is_stable_and_covers_all_splits():
    texts = [f"sentence number {i}" for i in range(2000)]
    s1 = [split_of(t) for t in texts]
    assert s1 == [split_of(t) for t in texts]
    counts = {k: s1.count(k) for k in ("train", "val", "test")}
    assert counts["train"] > 1700 and counts["val"] > 40 and counts["test"] > 40


def test_leak_filter_removes_eval_sources():
    exs = [TaskExample("correct_grammar", "She go to school every day.", "She goes to school every day.", "x"),
           TaskExample("correct_grammar", "He go home.", "He goes home.", "x")]
    kept, dropped = remove_leaks(exs, eval_user_texts())
    assert dropped == 1 and kept[0].source == "He go home."


def test_faithfulness_filter():
    assert is_faithful(TaskExample("formal", "can u send me the file by friday", "Could you please send me the file by Friday?", "x"))
    assert not is_faithful(TaskExample("casual", "send the file",
                                       "Hey! Hope your weekend went great. Could you send the file over soon?", "x"))


# ───────────── hand-written data is held out from the evaluation ─────────────

def test_conversation_data_excludes_eval_prompts():
    banned = _eval_norms()
    for text in all_conversation_user_texts():
        assert norm(text) not in banned, text


def test_handwritten_task_sources_exclude_eval_texts():
    banned = _eval_norms()
    hits = [ex.source for ex in handwritten_task_examples() + polite_examples() if norm(ex.source) in banned]
    assert hits == [], hits
    assert not any(norm(inf) in banned for inf, _ in POLITE_PAIRS)


def test_eval_context_chains_are_not_in_training_templates():
    assert "Python" not in LEARNING                                  # B1 chain held out
    assert not any(tool == "Flutter" for _, tool, _, _ in BUILD)     # B2 chain held out
    assert not any("exam" in event for event, _, _ in PROBLEMS)      # B3 chain held out


def test_conversation_data_has_no_emojis_ai_disclaimers_or_self_intros_in_greetings():
    emo = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
    for conv in build_conversation_conversations(repeats=1):
        for m in conv:
            assert not emo.search(m["content"])
            assert "as an ai" not in m["content"].lower()
        if conv[0]["content"].lower().startswith(("hi", "hey", "hello", "good morning")):
            assert "hibari" not in conv[1]["content"].lower()


# ───────────── evaluation suite ─────────────

def test_suite_covers_all_brief_categories():
    cats = {c.category for c in CASES}
    assert cats == set(CATEGORY_ORDER)
    assert len({c.id for c in CASES}) == len(CASES)
    counts = {cat: sum(c.category == cat for c in CASES) for cat in CATEGORY_ORDER}
    assert counts == {"basic": 6, "context": 3, "rephrase": 5, "formal": 4, "casual": 3, "grammar": 5,
                      "preservation": 3, "robustness": 7, "spec_examples": 7, "dialogue": 11}
    for c in CASES:
        assert c.checks and all(0 <= i < len(c.turns) for i in c.checks)


@pytest.mark.parametrize("case", [c for c in CASES if any(ch.reference for ch in c.checks.values())], ids=lambda c: c.id)
def test_reference_rewrites_pass_their_own_case(case):
    """Sanity: every case is passable — the hand-written reference passes."""
    for i, chk in case.checks.items():
        res = score_turn(chk, chk.reference, case.turns[i])
        assert res["passed"], (case.id, res["failed_checks"])


@pytest.mark.parametrize("case_id,bad", [
    ("C1", "Here's a revised version: I have been learning programming for two years."),  # lead
    ("C5", "we are planning to develop a new software for our college."),                  # unchanged
    ("F1", "She went to school every day."),                                               # wrong correction
    ("G1", "The meeting is scheduled for Tuesday at 10 AM."),                              # changed day
    ("G2", "The project contains three modules."),                                         # dropped fact
    ("D1", "Task: Make formal Input: I need leave tomorrow."),                             # format leak
    ("S1", "I'm doing well today. I'm doing well today."),                                 # repetition
    ("H7", "He left the keys there after his parents came."),                              # invented details
])
def test_typical_failures_are_caught(case_id, bad):
    case = next(c for c in CASES if c.id == case_id)
    i, chk = next(iter(case.checks.items()))
    assert not score_turn(chk, bad, case.turns[i])["passed"]


def test_self_introduction_and_echo_fail_chat_checks():
    case = next(c for c in CASES if c.id == "A1")
    chk = case.checks[0]
    assert not score_turn(chk, "Hello! I'm Hibari Koto, your AI friend.", "Hello!")["passed"]
    assert score_turn(chk, "Hi! How are you doing today?", "Hello!")["passed"]


# ───────────── training entry point ─────────────

def _tiny_setup(tmp_path, init=None):
    from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
    from koto.paths import TOKENIZER_DIR

    data = tmp_path / "data"
    data.mkdir()
    conv = {"source": "t", "messages": [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                                         {"role": "user", "content": "Task: Rephrase\nInput: she go home"},
                                         {"role": "assistant", "content": "She goes home."}]}
    (data / "train_conversations.json").write_text(json.dumps([conv] * 8))
    (data / "val_conversations.json").write_text(json.dumps([conv] * 2))
    model_cfg = tmp_path / "model.yaml"
    model_cfg.write_text(yaml.safe_dump({"model_name": "tiny", "vocab_size": 4096, "max_seq_len": 64, "d_model": 32,
                                         "n_layers": 1, "n_heads": 2, "d_ff": 64}))
    train_cfg = tmp_path / "train.yaml"
    cfg = {"experiment": "test-run", "data_cache_dir": str(data), "max_steps": 2, "batch_size": 4, "warmup_steps": 1,
           "eval_every": 2, "checkpoint_every": 2, "log_every": 1, "output_dir": str(tmp_path / "out"), "val_examples": 2}
    if init:
        cfg["init_checkpoint"] = init
    train_cfg.write_text(yaml.safe_dump(cfg))
    return str(model_cfg), str(train_cfg), str(TOKENIZER_DIR)


def test_train_script_runs_and_records_experiment(tmp_path):
    from training.train import train

    m, t, tok = _tiny_setup(tmp_path)
    train(model_config_path=m, training_config_path=t, tokenizer_dir=tok)
    hist = json.loads((tmp_path / "out" / "training_history.json").read_text())
    assert hist["metadata"]["experiment"] == "test-run"
    assert hist["metadata"]["koto_version"] == koto.__version__
    assert hist["metadata"]["model_version"] == koto.__version__  # no model_version in the test config
    assert hist["best"]["final_step"] == 2


def test_train_script_refuses_missing_init_checkpoint(tmp_path):
    from training.train import train

    m, t, tok = _tiny_setup(tmp_path, init=str(tmp_path / "missing.pt"))
    with pytest.raises(FileNotFoundError):
        train(model_config_path=m, training_config_path=t, tokenizer_dir=tok)


def test_all_tasks_have_natural_asks():
    assert set(NATURAL_ASKS) == set(TASKS)


def test_dialogue_eval_prompts_are_held_out_from_dialogue_skill_data():
    from koto.data.dialogue_skills import build_dialogue_skill_conversations
    from koto.data.tasks import norm

    train_users = {norm(m["content"]) for convs in build_dialogue_skill_conversations().values()
                   for c in convs for m in c if m["role"] == "user"}
    for case in CASES:
        if case.category == "dialogue":
            for t in case.turns:
                assert norm(t) not in train_users, (case.id, t)


# ───────────── data provenance guard (Koto 1.3.0 trained on the wrong data, EXP-0006) ─────────────

def _set_fingerprint(train_cfg_path, **fp):
    cfg = yaml.safe_load(open(train_cfg_path))
    cfg["data_fingerprint"] = fp
    open(train_cfg_path, "w").write(yaml.safe_dump(cfg))


def test_train_refuses_data_cache_dir_that_differs_from_the_config(tmp_path):
    from training.train import train

    m, t, tok = _tiny_setup(tmp_path)
    other = tmp_path / "other_data"
    other.mkdir()
    with pytest.raises(SystemExit, match="differs from data_cache_dir"):
        train(model_config_path=m, training_config_path=t, tokenizer_dir=tok, data_cache_dir=str(other))
    assert not (tmp_path / "out").exists()


def test_train_refuses_data_that_does_not_match_the_fingerprint(tmp_path):
    from training.train import train

    m, t, tok = _tiny_setup(tmp_path)
    _set_fingerprint(t, train_conversations=93509, val_conversations=2)
    with pytest.raises(SystemExit, match="train_conversations: expected 93509, found 8"):
        train(model_config_path=m, training_config_path=t, tokenizer_dir=tok)
    assert not (tmp_path / "out").exists()


def test_train_accepts_matching_fingerprint_and_records_conversation_counts(tmp_path):
    import hashlib
    from training.train import train

    m, t, tok = _tiny_setup(tmp_path)
    sha = hashlib.sha256((tmp_path / "data" / "train_conversations.json").read_bytes()).hexdigest()
    _set_fingerprint(t, train_conversations=8, val_conversations=2, train_sha256=sha)
    train(model_config_path=m, training_config_path=t, tokenizer_dir=tok)
    meta = json.loads((tmp_path / "out" / "training_history.json").read_text())["metadata"]
    assert meta["train_conversations"] == 8 and meta["val_conversations"] == 2
    assert meta["data_fingerprint_checked"] is True and meta["train_file_sha256"] == sha


def test_every_large_training_config_from_1_3_1_pins_its_data():
    from koto.paths import KOTO_ROOT

    for name in ["koto_1.3.1_large.yaml"]:
        cfg = yaml.safe_load(open(KOTO_ROOT / "configs" / "training" / name))
        assert cfg["data_cache_dir"] and set(cfg["data_fingerprint"]) == {"train_conversations", "val_conversations", "train_sha256"}
