"""Regression tests for bugs carried over from the v0.1 extraction."""

import pytest

from compareexpressions.slr_parsing import (
    ExprNode,
    SLR_expression_parser,
    SLR_Parser,
    Token,
    group,
    new_root_on_error,
    operate,
    tag_transfer,
)


def leaf(label, content="x"):
    return ExprNode(Token(label, content, content, 0, 0), [])


class TestExprNodeTags:
    def test_nodes_without_tag_handler_do_not_share_tags(self):
        a, b = leaf("A"), leaf("B")
        a.tags.add("X")
        assert b.tags == set()

    def test_copy_does_not_share_tags(self):
        node = leaf("A")
        node.tags.add("X")
        clone = node.copy()
        clone.tags.add("Y")
        assert node.tags == {"X"}

    def test_inherited_tags_are_not_shared_with_the_child(self):
        child = leaf("A")
        child.tags.add("X")
        parent = ExprNode(Token("P", "p", "p", 0, 0), [child], tag_handler=tag_transfer)
        parent.tags.add("Y")
        assert child.tags == {"X"}

    def test_str_shows_a_single_tag(self):
        node = leaf("A")
        node.tags = {"X"}
        assert str(node) == "A: x tags: {'X'}"


class TestExpressionParserBuilder:
    def test_custom_expression_node_symbol_is_not_a_literal_token(self):
        # The expression-node symbol ("E") must only exist in the grammar; an "E"
        # in the input is ordinary (undefined) text.
        parser = SLR_expression_parser(
            infix_operators=[("+", "ADD")],
            undefined=("O", "OTHER"),
            expression_node=("E", "EXPRESSION_NODE"),
        )
        tokens = parser.scan("2E+x")
        assert [(t.label, t.content) for t in tokens] == [("OTHER", "2E"), ("ADD", "+"), ("OTHER", "x")]
        assert parser.parse(tokens)[0].content_string() == "2E+x"


class TestParserConstruction:
    def test_token_list_argument_is_not_mutated(self):
        token_list = [("START", "START"), ("END", "END"), ("NULL", "NULL"), ("E", "E"), (" *\\+ *", "+"), ("x", "x")]
        before = list(token_list)
        SLR_Parser(token_list, [("START", "E", None), ("E", "E+E", None), ("E", "x", None)], "START", "END", "NULL")
        assert token_list == before

    def test_scan_rejects_unknown_mode(self):
        parser = SLR_expression_parser(infix_operators=[("+", "ADD")])
        with pytest.raises(ValueError, match="mode"):
            parser.scan("1+2", mode="nonsense")

    def test_productions_with_the_same_body_keep_their_own_actions(self):
        # S -> A y | B z ; A -> x ; B -> x. Both "x" reductions share a body, and
        # each must run its own action (reductions used to be keyed by body).
        calls = []

        def record(name):
            def action(production, output, tag_handler):
                calls.append(name)
                return output

            return action

        symbols = ["START", "END", "NULL", "S", "A", "B", "x", "y", "z"]
        parser = SLR_Parser(
            [(s, s) for s in symbols],
            [
                ("START", "S", record("START")),
                ("S", "Ay", record("S->Ay")),
                ("S", "Bz", record("S->Bz")),
                ("A", "x", record("A->x")),
                ("B", "x", record("B->x")),
            ],
            "START",
            "END",
            "NULL",
        )
        parser.parse(parser.scan("xy"))
        assert calls == ["A->x", "S->Ay"]

    @pytest.mark.parametrize("action", [group, operate])
    def test_actions_reject_zero_elements(self, action):
        with pytest.raises(ValueError):
            action(0)


class TestErrorRecovery:
    def test_new_root_on_error_starts_a_new_root_at_the_offending_token(self):
        parser = SLR_expression_parser(
            infix_operators=[("+", "ADD")],
            delimiters=[(("(", ")"), group(1))],
            error_handler=[(lambda items, next_symbol: next_symbol.label == "START_DELIMITER", new_root_on_error)],
        )
        output = parser.parse(parser.scan("(1+2)(3)"))
        assert [node.content_string() for node in output] == ["(1+2)", "(3)"]
