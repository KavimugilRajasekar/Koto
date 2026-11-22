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

FAMILIES = build_behaviour_conversations(seed=123)
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
    train_users = {norm(m["content"]) for convs in FAMILIES.values() for c in convs for m in c if m["role"] == "user"}
    leaked = [t for t in eval_user_texts() if len(norm(t).split()) >= 3 and norm(t) in train_users]
    assert not leaked, leaked


def test_identity_v2_rewrite():
    assert identity_v2("I'm Hibari Koto. You can call me Hibari.") == "I'm Koto. You can call me Koto."
    conv = [{"role": "user", "content": "Hibari Koto?"}, {"role": "assistant", "content": "My name is Hibari Koto, but Hibari is fine."}]
    out = apply_identity_v2(conv)
    assert out[0]["content"] == "Hibari Koto?"                      # user turns untouched
    assert "Hibari Koto" not in out[1]["content"] and "Koto" in out[1]["content"]
    for c in FAMILIES["identity_v2"]:
        assert "Hibari Koto" not in c[-1]["content"]


def test_1_2_0_configs_agree():
    data = yaml.safe_load((KOTO_ROOT / "configs/data/koto_1.2.0.yaml").read_text())
    train = yaml.safe_load((KOTO_ROOT / "configs/training/koto_1.2.0.yaml").read_text())
    prof = ModelProfile.load(KOTO_ROOT / "configs/release/koto_1.2.0.yaml")
    assert data["system_prompt"].strip() == prof.system_prompt == prof.training_system_prompt.strip() == SYSTEM_PROMPT_V2
    assert data["identity"] == "v2"
    assert str(train["model_version"]) == prof.weights_version == prof.version == "1.2.0"
    assert train["data_cache_dir"] == data["out_dir"]
    assert prof.training_status == "NOT_STARTED"
    assert not (KOTO_ROOT / train["output_dir"] / "best_model.pt").exists() or prof.checkpoint_sha256


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
