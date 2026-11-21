"""Tests for the evaluation suite: held-out prompts and metric helpers."""

import re

from hibari.data.curated import FACTS, INTENTS, MULTI_TURN, all_curated_user_texts, build_curated_conversations
from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
from hibari.evaluation.suite import CASES, EvalCase, grammar_heuristic, ngram_repetition, score_case


def _norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def test_eval_prompts_are_held_out_from_curated_training_data():
    train = {_norm(t) for t in all_curated_user_texts()}
    for case in CASES:
        for role, text in case.turns:
            if role == "user":
                assert _norm(text) not in train, f"{case.id}: eval prompt appears in curated training data: {text!r}"


def test_rewrite_eval_prompts_are_held_out_from_rewrite_training_data():
    from hibari.data.rewrite import all_rewrite_user_texts, build_polite_conversations

    train_texts = [_norm(t) for t in all_rewrite_user_texts()]
    train_users = {_norm(c[0]["content"]) for c in build_polite_conversations()}
    for case in CASES:
        if case.category != "rewrite":
            continue
        user = _norm(case.final_user)
        assert user not in train_users, f"{case.id}: rewrite eval prompt appears in training data"
        for t in train_texts:
            assert t not in user, f"{case.id}: contains training text {t!r}"


def test_rewrite_data_shapes():
    import random

    from hibari.data.rewrite import POLITE_LEAD, build_polite_conversations, coedit_to_conversations

    convs = build_polite_conversations(n_templated=20, n_emails=10)
    assert all(len(c) == 2 and c[0]["role"] == "user" and c[1]["role"] == "assistant" for c in convs)
    assert any(c[1]["content"].startswith(POLITE_LEAD) for c in convs)
    assert any("Subject:" in c[1]["content"] for c in convs)
    rows = [
        {"task": "gec", "src": "Fix grammar: He go home.", "tgt": "He goes home."},
        {"task": "gec", "src": "Fix grammar: It is fine.", "tgt": "It is fine."},
        {"task": "neutralize", "src": "Remove bias: x", "tgt": "y"},
    ]
    out = coedit_to_conversations(rows, random.Random(0))
    assert len(out) == 2
    assert out[0][1]["content"].endswith("He goes home.")
    assert out[1][1]["content"].startswith("It already looks correct:")


def test_eval_suite_covers_all_categories():
    cats = {c.category for c in CASES}
    assert cats == {"basic", "context", "emotional", "language", "informal", "knowledge", "safety", "robustness", "rewrite"}
    assert len({c.id for c in CASES}) == len(CASES)


def test_curated_data_has_no_emojis_and_valid_roles():
    convs = build_curated_conversations(DEFAULT_SYSTEM_PROMPT)
    emo = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
    for c in convs:
        assert c[0]["role"] == "system"
        roles = [m["role"] for m in c[1:]]
        assert roles[0] == "user" and roles[-1] == "assistant"
        assert all(a != b for a, b in zip(roles, roles[1:]))
        assert not any(emo.search(m["content"]) for m in c)


def test_metric_helpers():
    assert ngram_repetition("a b c a b c a b c") > 0.3
    assert ngram_repetition("I like reading books on rainy days.") == 0.0
    g = grammar_heuristic("I'm fine, thanks.")
    assert all(g.values())
    assert not grammar_heuristic("i am the the best")["no_doubled_word"]
    s = score_case(EvalCase("x", "basic", [("user", "hi")], [r"\bhello\b"]), "Hello there.", True)
    assert s["relevant"] and s["complete"] and not s["repetitive"]
