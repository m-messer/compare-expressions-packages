"""Exceptions raised by the expression_parsing package."""

from __future__ import annotations

from .feedback import FeedbackTag


class ExpressionParsingError(ValueError):
    """An expression or its parsing parameters could not be parsed."""


class SymbolAssumptionError(ExpressionParsingError):
    """A ``symbol_assumptions`` parameter is malformed or names an invalid assumption."""


class LatexParseError(ExpressionParsingError):
    """A LaTeX expression (or a symbol's LaTeX) could not be parsed."""


class ExpressionSyntaxError(ExpressionParsingError):
    """A response could not be parsed; ``feedback`` is the tag to show the learner."""

    def __init__(self, feedback: FeedbackTag) -> None:
        super().__init__(f"{feedback.tag}: {dict(feedback.inputs)}")
        self.feedback = feedback
