"""Exceptions raised by the expression_parsing package."""


class ExpressionParsingError(ValueError):
    """An expression or its parsing parameters could not be parsed."""


class SymbolAssumptionError(ExpressionParsingError):
    """A ``symbol_assumptions`` parameter is malformed or names an invalid assumption."""


class LatexParseError(ExpressionParsingError):
    """A LaTeX expression (or a symbol's LaTeX) could not be parsed."""
