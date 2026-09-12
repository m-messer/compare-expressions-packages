"""String-level preprocessing of responses before they are parsed."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .feedback import FeedbackTag, FeedbackTagName
from .substitution import substitute_input_symbols

if TYPE_CHECKING:
    from .params import ExpressionParams

_BRACKET_PAIRS = {")": "(", "]": "[", "}": "{"}
_GROUPING = "()[]{}"


def find_matching_parenthesis(string: str, index: int, delimiters: tuple[str, str] = ("(", ")")) -> int:
    """Index of the delimiter closing the one at (or first after) ``index``; ``-1`` if unclosed."""
    opening, closing = delimiters
    depth = 0
    for k in range(index, len(string)):
        if string[k] == opening:
            depth += 1
        elif string[k] == closing:
            depth -= 1
            if depth == 0:
                return k
    return -1


def has_matching_brackets(expr: str) -> bool:
    """True if every ``(``, ``[``, ``{`` is closed by the same kind, correctly nested.

    Mismatched kinds (e.g. the ``[x+y)`` of interval notation) and unbalanced
    brackets are rejected.
    """
    stack = []
    for char in expr:
        if char in "([{":
            stack.append(char)
        elif char in ")]}" and (not stack or stack.pop() != _BRACKET_PAIRS[char]):
            return False
    return not stack


def is_multiple_answers_wrapper(expr: str) -> bool:
    """True if ``expr`` as a whole is one top-level ``{...}``: a set of acceptable answers.

    Braces that merely sit at both ends (e.g. ``{x+1}*{x-2}``) don't count.
    """
    stripped = expr.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return False
    return find_matching_parenthesis(stripped, 0, delimiters=("{", "}")) == len(stripped) - 1


def create_expression_set(exprs: str | Sequence[str], params: ExpressionParams) -> list[str]:
    """Expand a response into the expressions it stands for.

    A top-level ``{a, b}`` gives one expression per element, and ``±``/``∓``
    (``plus_minus``/``minus_plus``) give both signs. Symbol aliases are
    substituted. The result is de-duplicated, in first-seen order.
    """
    if isinstance(exprs, str):
        exprs = [e.strip() for e in exprs[1:-1].split(",")] if is_multiple_answers_wrapper(exprs) else [exprs]
    expanded: dict[str, None] = {}
    for original in exprs:
        expr = substitute_input_symbols(original, params)[0]
        if params.plus_minus is not None:
            expr = expr.replace(params.plus_minus, "plus_minus")
        if params.minus_plus is not None:
            expr = expr.replace(params.minus_plus, "minus_plus")
        if "plus_minus" in expr or "minus_plus" in expr:
            for plus_minus, minus_plus in (("+", "-"), ("-", "+")):
                signed = expr.replace("plus_minus", plus_minus).replace("minus_plus", minus_plus).strip()
                expanded[signed.lstrip("+").strip()] = None
        else:
            expanded[expr] = None
    return list(expanded)


def convert_bracket_notation(expr: str) -> tuple[str, FeedbackTag | None]:
    """Accept ``[]`` and ``{}`` as grouping brackets by rewriting them as ``()``.

    SymPy reserves ``[]`` and ``{}`` for lists and sets. A ``{}`` spanning the
    whole expression is kept, as it denotes a set of acceptable answers (see
    :func:`create_expression_set`). Brackets must be closed with the same
    kind: for mismatched brackets (e.g. ``[x+y)``) the expression is returned
    unchanged with ``BRACKET_NOTATION_MISMATCH`` feedback.
    """
    if not has_matching_brackets(expr):
        return expr, FeedbackTag(FeedbackTagName.BRACKET_NOTATION_MISMATCH, {"x": expr})
    expr = expr.replace("[", "(").replace("]", ")")
    if is_multiple_answers_wrapper(expr):
        return expr, None
    return expr.replace("{", "(").replace("}", ")"), None


def convert_absolute_notation(expr: str, name: str) -> tuple[str, FeedbackTag | None]:
    """Rewrite ``|x|`` as ``Abs(x)``.

    Nested ``|`` cannot be handled: each ``|`` is paired with the closest one
    to its right, and ``ABSOLUTE_VALUE_NOTATION_AMBIGUITY`` feedback (naming
    ``name``, e.g. ``"response"``) is returned when that guess was needed.
    """
    n_pipes = expr.count("|")
    ambiguous: list[int] = []
    if n_pipes == 2:
        chars = list(expr)
        chars[chars.index("|")] = "Abs("
        chars[chars.index("|")] = ")"
        expr = "".join(chars)
    elif n_pipes > 0:
        starts: list[int] = []
        ends: list[int] = []

        def grouping(char: str) -> bool:
            return char.isalnum() or char in _GROUPING

        if expr[0] == "|":
            starts.append(0)
        for i in range(1, len(expr) - 1):
            if expr[i] == "|":
                if grouping(expr[i - 1]) and not grouping(expr[i + 1]):
                    ends.append(i)
                elif grouping(expr[i + 1]) and not grouping(expr[i - 1]):
                    starts.append(i)
                else:
                    ambiguous.append(i)
        if expr[-1] == "|":
            ends.append(len(expr) - 1)
        chars = list(expr)
        for i in starts:
            chars[i] = "Abs("
        for i in ends:
            chars[i] = ")"
        k = 0
        previous_ambiguous = -1
        for i in ambiguous:
            previous_start = max((j for j in starts if j < i), default=-1)
            previous_end = max((j for j in ends if j < i), default=-1)
            latest = max(previous_start, previous_end, previous_ambiguous)
            # chars[i - 1] may already be a replacement ("Abs(" or ")"), which is not alphanumeric
            opening = "*Abs(" if chars[i - 1].isalnum() else "Abs("
            if latest == previous_end:
                chars[i] = opening
            elif latest == previous_ambiguous:
                chars[i] = opening if k % 2 == 0 else ")"
                k += 1
            else:
                chars[i] = ")"
            previous_ambiguous = i
        expr = "".join(chars)

    if n_pipes > 2 and ambiguous:
        return expr, FeedbackTag(FeedbackTagName.ABSOLUTE_VALUE_NOTATION_AMBIGUITY, {"name": name})
    return expr, None


@dataclass(frozen=True)
class Preprocessed:
    """A preprocessed expression and the feedback raised while preprocessing it."""

    expression: str
    feedback: FeedbackTag | None = None

    @property
    def success(self) -> bool:
        return self.feedback is None


def preprocess_expression(name: str, expr: str, params: ExpressionParams) -> Preprocessed:
    """Substitute symbol aliases and rewrite bracket and absolute-value notation.

    ``name`` (e.g. ``"response"``) is used in feedback. Bracket feedback takes
    precedence over absolute-value feedback.
    """
    expr = substitute_input_symbols(expr.strip(), params)[0]
    bracket_feedback = None
    if not params.strict_syntax:
        expr, bracket_feedback = convert_bracket_notation(expr)
    expr, abs_feedback = convert_absolute_notation(expr, name)
    return Preprocessed(expr, bracket_feedback or abs_feedback)
