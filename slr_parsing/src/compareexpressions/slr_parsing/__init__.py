"""Generic SLR(1) parser engine.

Extracted from compareExpressions (app/utility/slr_parsing_utilities.py).
Self-contained: depends only on the standard library.
"""

from .actions import (
    append,
    append_last,
    compose,
    create_node,
    flatten,
    group,
    infix,
    insert_infix,
    join,
    operate,
    proceed,
    relabel,
)
from .builder import SLR_expression_parser
from .errors import new_root_on_error
from .grammar import catch_undefined
from .parser import SLR_Parser
from .tags import (
    tag,
    tag_removal,
    tag_replace,
    tag_rule_intersection,
    tag_rule_union,
    tag_transfer,
)
from .tokens import (
    ExprNode,
    Token,
    traverse_group,
    traverse_infix,
    traverse_postfix,
    traverse_prefix,
)

__all__ = [
    "catch_undefined",
    "proceed",
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
    "SLR_expression_parser",
    "Token",
    "ExprNode",
    "SLR_Parser",
]
