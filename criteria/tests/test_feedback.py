"""Tests for the feedback helpers that replace evaluation_result's criteria support."""

import json

import pytest

from compareexpressions.criteria import CriteriaGraph
from compareexpressions.criteria.feedback import add_feedback_from_tags, criteria_test_data, resolve_feedback


class RecordingResult:
    """Minimal ResultLike: tags derive from the feedback added, like lf_toolkit's Result."""

    def __init__(self):
        self.feedback = {}

    @property
    def tags(self):
        return list(self.feedback)

    def add_feedback(self, tag, feedback):
        self.feedback.setdefault(tag, []).append(feedback)


def graph_with_feedback():
    graph = CriteriaGraph("g")
    graph.add_evaluation_node("EQ", "response = answer", "compare")
    graph.attach("EQ", "EQ_TRUE", summary="true", details="true", feedback_string_generator=lambda inputs: " Correct! ")
    graph.attach(
        "EQ", "EQ_FALSE", summary="false", details="false", feedback_string_generator=lambda inputs: inputs["why"]
    )
    graph.attach("EQ", "EQ_SILENT", summary="silent", details="silent", feedback_string_generator=lambda inputs: None)
    return graph


class TestResolveFeedback:
    def test_generators_receive_inputs_and_text_is_stripped(self):
        resolved = resolve_feedback(graph_with_feedback(), {"EQ_TRUE": None, "EQ_FALSE": {"why": "x != y"}})
        assert resolved == [("EQ_TRUE", "Correct!"), ("EQ_FALSE", "x != y")]

    def test_none_feedback_resolves_to_empty_text(self):
        assert resolve_feedback(graph_with_feedback(), {"EQ_SILENT": None}) == [("EQ_SILENT", "")]

    def test_custom_feedback_overrides_generator(self):
        resolved = resolve_feedback(graph_with_feedback(), {"EQ_TRUE": None}, custom_feedback={"EQ_TRUE": "Well done"})
        assert resolved == [("EQ_TRUE", "Well done")]


class TestAddFeedbackFromTags:
    def test_records_every_tag_including_blank_feedback(self):
        result = RecordingResult()
        add_feedback_from_tags(result, {"EQ_TRUE": None, "EQ_SILENT": None}, graph_with_feedback())
        assert result.tags == ["EQ_TRUE", "EQ_SILENT"]
        assert result.feedback == {"EQ_TRUE": ["Correct!"], "EQ_SILENT": [""]}

    def test_tags_already_on_the_result_are_skipped(self):
        result = RecordingResult()
        result.add_feedback("EQ_TRUE", "first")
        add_feedback_from_tags(result, {"EQ_TRUE": None}, graph_with_feedback())
        assert result.feedback == {"EQ_TRUE": ["first"]}


def test_criteria_test_data():
    graph = graph_with_feedback()
    data = criteria_test_data({"main": graph})
    assert set(data) == {"criteria_graphs", "criteria_graphs_vis"}
    assert "EQ" in json.loads(data["criteria_graphs"]["main"])["evaluations"]
    assert data["criteria_graphs_vis"]["main"].startswith("flowchart TD")


class TestLfToolkitCompatibility:
    """The helpers are written against a Protocol; check the real lf_toolkit Result fits it."""

    def test_feedback_lands_on_an_lf_toolkit_result(self):
        evaluation = pytest.importorskip("lf_toolkit.evaluation")
        result = evaluation.Result()
        add_feedback_from_tags(result, {"EQ_TRUE": None, "EQ_FALSE": {"why": "x != y"}}, graph_with_feedback())
        assert result.tags == ["EQ_TRUE", "EQ_FALSE"]
        assert result.feedback == "Correct!<br>x != y"
