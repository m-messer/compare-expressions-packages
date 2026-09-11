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
from .builder import build_expression_parser
from .errors import new_root_on_error
from .grammar import catch_undefined
from .parser import SLRParser
from .tags import (
    add_tag,
    remove_tag,
    replace_tag,
    intersection_rule,
    union_rule,
    inherit_tags,
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
    "union_rule",
    "intersection_rule",
    "inherit_tags",
    "remove_tag",
    "add_tag",
    "replace_tag",
    "traverse_prefix",
    "traverse_postfix",
    "traverse_infix",
    "traverse_group",
    "new_root_on_error",
    "build_expression_parser",
    "Token",
    "ExprNode",
    "SLRParser",
]
