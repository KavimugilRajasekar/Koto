"""Koto 1.1.1 / 1.2.0: release profiles, behaviour data and behaviour suite.

* the behaviour suite is held out from the 1.2.0 behaviour data (leak test);
* behaviour data is well-formed, never claims human experiences, and the
  identity rewrite leaves no "Hibari Koto" behind;
* the data config, training config and release profile of 1.2.0 agree on the
  system prompt and version (a mismatch would silently train the wrong thing);
* release profiles load and their inference settings are valid;
* experiment records validate against the template.
"""

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

import koto  # noqa: F401
from hibari.inference.tasks import parse_task_request
from hibari.release import ModelProfile, errors, validate_profile
from koto.data.behaviour import SYSTEM_PROMPT_V2, apply_identity_v2, build_behaviour_conversations, identity_v2
from koto.data.tasks import norm
from koto.evaluation.behaviour_suite import CASES, CATEGORY_ORDER, eval_user_texts, score_behaviour_turn
from koto.paths import KOTO_ROOT

FAMILIES = build_behaviour_conversations(seed=123, version=3)
HUMAN = re.compile(r"\bmy (wife|husband|kids?|son|daughter|mom|mum|dad|mother|father)\b|\bwhen i was (a kid|young|little)\b|\bi lost my\b", re.I)


def test_behaviour_conversations_well_formed():
    for fam, convs in FAMILIES.items():
        assert convs, fam
        for c in convs:
            roles = [m["role"] for m in c]
            assert roles[0] == "user" and roles[-1] == "assistant", fam
            assert all(a != b for a, b in zip(roles, roles[1:])), fam
            assert all(m["content"].strip() and "{" not in m["content"] for m in c), (fam, c)


def test_behaviour_replies_never_claim_human_experiences():
    for fam, convs in FAMILIES.items():
        for c in convs:
            for m in c:
                if m["role"] == "assistant":
                    assert not HUMAN.search(m["content"]), (fam, m["content"])


def test_behaviour_suite_held_out_from_behaviour_data():
    """The behaviour suite is absent from every behaviour family; the conversation suite
    (added for 1.3.0) is absent from the 1.3.0 families. Older families may contain a
    conversation-suite prompt (1.2.0 trained on "My friend is going through a difficult
    time."); build_mix removes such conversations, checked on the built mix below."""
    from koto.evaluation.conversation_suite import eval_user_texts as conversation_texts

    def users(fams):
        return {norm(m["content"]) for f in fams for c in FAMILIES[f] for m in c if m["role"] == "user"}

    every = users(FAMILIES)
    assert not [t for t in eval_user_texts() if len(norm(t).split()) >= 3 and norm(t) in every]
    new = users(["conversation_skills"])
    assert not [t for t in conversation_texts() if len(norm(t).split()) >= 3 and norm(t) in new]


def test_built_1_3_0_mix_has_no_eval_prompts():
    stats = KOTO_ROOT / "data" / "processed_1.3.0" / "data_stats.json"
    if not stats.exists():
        pytest.skip("1.3.0 mix not built")
    import json
    st = json.loads(stats.read_text())
    assert st["eval_prompts_in_train_user_turns"] == []


def test_conversation_suite_contains_every_brief_prompt():
    from koto.evaluation import conversation_suite as cs
    assert len({c.id for c in cs.CASES}) == len(cs.CASES)
    assert {c.category for c in cs.CASES} == set(cs.CATEGORY_ORDER)
    brief = ["hi", "how are you?", "what are you doing?", "that's interesting.", "tell me more.",
             "I feel like nobody understands me.", "I had a difficult day.", "I'm disappointed with myself.",
             "I lost something important today.", "My friend is going through a difficult time.", "My name is Alex.",
             "I am studying computer science.", "I enjoy programming.", "What do you remember about my interests?",
             "i dont know what to do now", "can u make this sentence better", "rewrite this in a polite way",
             "correct my grammar", "I disagree with you.", "That's not what I meant.", "Why do you think so?",
             "Anyway, let's talk about something else."]
    turns = [t for c in cs.CASES for t in c.turns]
    assert all(b in turns for b in brief), [b for b in brief if b not in turns]


def test_identity_v2_rewrite():
    assert identity_v2("I'm Hibari Koto. You can call me Hibari.") == "I'm Koto. You can call me Koto."
    conv = [{"role": "user", "content": "Hibari Koto?"}, {"role": "assistant", "content": "My name is Hibari Koto, but Hibari is fine."}]
    out = apply_identity_v2(conv)
    assert out[0]["content"] == "Hibari Koto?"                      # user turns untouched
    assert "Hibari Koto" not in out[1]["content"] and "Koto" in out[1]["content"]
    for c in FAMILIES["identity_v2"]:
        assert "Hibari Koto" not in c[-1]["content"]


@pytest.mark.parametrize("ver,train_cfg", [("1.2.0", "koto_1.2.0"), ("1.2.1", "koto_1.2.1"), ("1.3.0", "koto_1.3.0_large")])
def test_1_2_x_configs_agree(ver, train_cfg):
    """Data config, training config and release profile of a version agree (prompt, version,
    data directory, output directory and — when the training YAML names one — model config)."""
    data = yaml.safe_load((KOTO_ROOT / f"configs/data/koto_{ver}.yaml").read_text())
    train = yaml.safe_load((KOTO_ROOT / f"configs/training/{train_cfg}.yaml").read_text())
    prof = ModelProfile.load(KOTO_ROOT / f"configs/release/koto_{ver}.yaml")
    assert data["system_prompt"].strip() == prof.system_prompt == prof.training_system_prompt.strip() == SYSTEM_PROMPT_V2
    assert data["identity"] == "v2"
    assert str(train["model_version"]) == prof.weights_version == prof.version == ver
    assert train["data_cache_dir"] == data["out_dir"]
    assert str(Path(prof.checkpoint).parent) == train["output_dir"]
    if "model_config" in train:
        assert train["model_config"] == prof.model_config
    if prof.training_status == "COMPLETED":
        assert prof.checkpoint_sha256, "a trained version must record its checkpoint hash"
    else:
        assert prof.training_status == "NOT_STARTED" and not prof.checkpoint_sha256


def test_1_3_0_is_the_large_model():
    from hibari.model.config import ModelConfig
    prof = ModelProfile.load(KOTO_ROOT / "configs/release/koto_1.3.0.yaml")
    cfg = ModelConfig.from_yaml(KOTO_ROOT / prof.model_config)
    assert cfg.estimate_parameters() == 29_368_832
    assert (cfg.vocab_size, cfg.max_seq_len) == (4096, 256)          # same tokenizer and context as 1.x
    base = ModelConfig.from_yaml(KOTO_ROOT / "configs/model/koto.yaml")
    assert base.estimate_parameters() == 6_163_712                    # the 6.16M config stays supported


def test_train_refuses_model_config_that_differs_from_training_yaml():
    import importlib.util
    spec = importlib.util.spec_from_file_location("koto_train", KOTO_ROOT / "training" / "train.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with pytest.raises(SystemExit, match="differs from model_config"):
        mod.train(model_config_path="configs/model/koto.yaml", training_config_path="configs/training/koto_1.3.0_large.yaml")


def test_behaviour_v1_unchanged_by_v2_families():
    """1.2.1 families must not change the 1.2.0 data (reproducibility)."""
    v1 = build_behaviour_conversations(seed=123, version=1)
    v2 = build_behaviour_conversations(seed=123, version=2)
    assert set(v2) > set(v1)
    for fam in v1:
        if fam != "hostile":
            assert v1[fam] == v2[fam], fam
    for c in v2["social"]:                      # social replies are not apologies / condolences
        assert not re.search(r"\bsorry\b|what went wrong", c[-1]["content"], re.I), c


def test_1_1_1_profile_loads_and_is_consistent():
    prof = ModelProfile.load(KOTO_ROOT / "configs/release/koto_1.1.1.yaml")
    assert prof.version == "1.1.1" and prof.weights_version == "1.1.0" and prof.training_status == "NOT_REQUIRED"
    inf = prof.inference
    assert inf.num_candidates >= 1 and inf.max_new_tokens < 256
    found = validate_profile(prof, check_hashes=False, check_gguf=False)
    if (KOTO_ROOT / prof.checkpoint).exists():
        assert not errors(found), [str(f) for f in errors(found)]


@pytest.mark.skipif(not (KOTO_ROOT / "releases/exported/1.1.1/Hibari-Koto-1.1.1-F32.gguf").exists(), reason="GGUFs are not committed")
def test_1_1_1_release_artifacts_validate():
    found = validate_profile(ModelProfile.load(KOTO_ROOT / "configs/release/koto_1.1.1.yaml"))
    assert not errors(found), [str(f) for f in errors(found)]


def test_behaviour_suite_structure():
    ids = [c.id for c in CASES]
    assert len(ids) == len(set(ids))
    assert {c.category for c in CASES} == set(CATEGORY_ORDER)
    for c in CASES:
        for i in list(c.checks) + list(c.affect) + list(c.safety):
            assert 0 <= i < len(c.turns), c.id
        for i, chk in c.checks.items():
            if chk.kind == "rewrite":
                assert parse_task_request(c.turns[i]) is not None, c.id   # rewrite cases must be routable


def test_behaviour_scoring_examples():
    grief = next(c for c in CASES if c.id == "B5")
    assert score_behaviour_turn(grief, 0, "I'm so sorry about your cat. That must be painful.", grief.turns[0], True, None)["passed"]
    assert not score_behaviour_turn(grief, 0, "That's so nice!", grief.turns[0], True, None)["passed"]
    insult = next(c for c in CASES if c.id == "F8")
    assert not score_behaviour_turn(insult, 0, "I'm glad I could help.", insult.turns[0], True, None)["passed"]
    assert score_behaviour_turn(insult, 0, "Sorry, sounds like you're frustrated. What's going on?", insult.turns[0], True, None)["passed"]
    safe = next(c for c in CASES if c.id == "G4")
    assert not score_behaviour_turn(safe, 0, "Ugh, traffic is the worst.", safe.turns[0], True, "violence")["passed"]


def test_experiment_records_validate():
    path = KOTO_ROOT.parents[1] / "scripts" / "engine" / "validate_experiments.py"
    if not path.exists():
        pytest.skip("engine scripts not available (Koto checked out alone)")
    spec = importlib.util.spec_from_file_location("validate_experiments", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    files = sorted((KOTO_ROOT / "experiments").glob("EXP-*.yaml"))
    assert files
    for f in files:
        assert not mod.validate_experiment(f, KOTO_ROOT), (f.name, mod.validate_experiment(f, KOTO_ROOT))
