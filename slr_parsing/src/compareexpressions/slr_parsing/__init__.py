"""Generic SLR(1) parser engine.

Extracted verbatim from compareExpressions (app/utility/slr_parsing_utilities.py).
Self-contained: depends only on the standard library.
"""

from .parser import (
    # Scanner / parser building blocks
    catch_undefined,
    proceed,
    package,
    append,
    append_last,
    join,
    create_node,
    relabel,
    group,
    operate,
    infix,
    insert_infix,
    compose,
    flatten,
    # Tag management
    tag_rule_union,
    tag_rule_intersection,
    tag_transfer,
    tag_removal,
    tag,
    tag_replace,
    # Node traversal
    traverse_prefix,
    traverse_postfix,
    traverse_infix,
    traverse_group,
    # Error handling
    new_root_on_error,
    discard_output_until_on_error,
    # Parser generator
    SLR_expression_parser,
    # Classes
    Token,
    ExprNode,
    SLR_Parser,
)

__all__ = [
    "catch_undefined",
    "proceed",
    "package",
    "append",
    "append_last",
    "join",
    "create_node",
    "relabel",
    "group",
    "operate",
    "infix",
    "insert_infix",
    "compose",
    "flatten",
    "tag_rule_union",
    "tag_rule_intersection",
    "tag_transfer",
    "tag_removal",
    "tag",
    "tag_replace",
    "traverse_prefix",
    "traverse_postfix",
    "traverse_infix",
    "traverse_group",
    "new_root_on_error",
    "discard_output_until_on_error",
    "SLR_expression_parser",
    "Token",
    "ExprNode",
    "SLR_Parser",
]
