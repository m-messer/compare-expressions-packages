"""Regression tests for bugs carried over from the v0.1 extraction."""

import pytest

from compareexpressions.criteria import CriteriaGraph, generate_criteria_parser
from compareexpressions.criteria import parsing as criteria_parsing


def small_graph():
    graph = CriteriaGraph("g")
    graph.add_evaluation_node("E1", "eval", "evaluate E1")
    graph.attach("E1", "C1", summary="crit", details="criterion C1")
    graph.add_output_node("OUT", "out", "done")
    graph.attach("C1", "OUT")
    return graph


class TestTreeRendering:
    @pytest.mark.xfail(strict=True, reason="v0.1 bug: Tree.mermaid() pops the tree's own children")
    def test_mermaid_does_not_consume_the_tree(self):
        tree = small_graph().build_tree("E1")
        first = tree.mermaid()
        assert len(tree.outgoing) == 1
        assert tree.mermaid() == first
        assert "C1" in first and "OUT" in first


class TestCriteriaParser:
    @pytest.mark.xfail(strict=True, reason="v0.1 bug: generate_criteria_parser appends to the module default list")
    def test_reserved_words_do_not_leak_between_parsers(self):
        before = len(criteria_parsing.base_token_list)
        generate_criteria_parser({"learner": {"response": None}})
        parser = generate_criteria_parser({"task": {"answer": None}})
        assert len(criteria_parsing.base_token_list) == before
        labels = [token.label for token in parser.scan("response = answer")]
        assert labels == ["OTHER", "EQUALITY", "RESERVED"]


class TestGraph:
    @pytest.mark.xfail(strict=True, reason="v0.1 bug: build_tree reads .label from None for unknown nodes")
    def test_build_tree_rejects_unknown_evaluation(self):
        with pytest.raises(ValueError, match="Unknown evaluation node NOPE"):
            small_graph().build_tree("NOPE")

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: add_node(Evaluation) reads a missing .sufficiencies")
    def test_add_node_accepts_evaluation_nodes(self):
        def evaluate(response):
            return {}

        graph = CriteriaGraph("g")
        graph.add_node(CriteriaGraph.Evaluation("E", "eval", "details", evaluate))
        assert graph.evaluations["E"].evaluate is evaluate

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: nodes define __eq__ without __hash__")
    def test_nodes_are_hashable_and_comparable_to_anything(self):
        node = small_graph().evaluations["E1"]
        assert node in {node}
        assert node != "E1"

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: generate_feedback prints graph internals on failure")
    def test_failing_evaluation_is_reported_without_printing(self, capsys):
        def broken(response):
            raise RuntimeError("boom")

        graph = CriteriaGraph("g")
        graph.add_evaluation_node("E1", "eval", "details", evaluate=broken)
        graph.attach("E1", "E1_TRUE", summary="true", details="true")
        with pytest.raises(Exception, match="E1") as info:
            graph.generate_feedback("x", "E1_TRUE")
        assert isinstance(info.value.__cause__, RuntimeError)
        assert capsys.readouterr().out == ""
