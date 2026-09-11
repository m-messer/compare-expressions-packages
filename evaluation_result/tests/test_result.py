"""Native tests for the evaluation_result package.

compareExpressions has no dedicated test for EvaluationResult, so these are
written fresh to cover feedback aggregation and serialisation.
"""

import pytest

from compareexpressions.evaluation_result import EvaluationResult


class TestEvaluationResult:
    def test_defaults(self):
        r = EvaluationResult()
        assert r.is_correct is False
        out = r.serialise()
        assert out["is_correct"] is False
        assert out["feedback"] == ""
        assert out["tags"] == []

    def test_add_feedback_records_tag_and_message(self):
        r = EvaluationResult()
        r.add_feedback(("MY_TAG", "hello"))
        assert r.get_feedback("MY_TAG") == [0]
        assert "MY_TAG" in r.get_tags()

    def test_add_feedback_requires_tuple(self):
        r = EvaluationResult()
        with pytest.raises(TypeError):
            r.add_feedback("not a tuple")

    def test_serialise_joins_feedback_with_br(self):
        r = EvaluationResult()
        r.add_feedback(("A", "first"))
        r.add_feedback(("B", "second"))
        out = r.serialise()
        assert out["feedback"] == "first<br>second"
        assert set(out["tags"]) == {"A", "B"}

    def test_same_tag_collects_multiple_indices(self):
        r = EvaluationResult()
        r.add_feedback(("DUP", "one"))
        r.add_feedback(("DUP", "two"))
        assert r.get_feedback("DUP") == [0, 1]

    def test_is_correct_roundtrips_through_serialise(self):
        r = EvaluationResult()
        r.is_correct = True
        assert r.serialise()["is_correct"] is True

    def test_getitem_exposes_serialised_fields(self):
        r = EvaluationResult()
        r.add_feedback(("T", "msg"))
        assert r["is_correct"] is False
        assert "msg" in r["feedback"]
