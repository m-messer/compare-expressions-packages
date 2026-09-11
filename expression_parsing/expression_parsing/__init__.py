"""SymPy-based expression parsing, preprocessing, and LaTeX preview.

Extracted from compareExpressions and decoupled from app-specific feedback
strings (see feedback.py / FeedbackTag). Modules:
- expression_utilities.py   <- app/utility/expression_utilities.py
- syntactical_comparison.py <- app/utility/syntactical_comparison_utilities.py
- preview_utilities.py      <- app/utility/preview_utilities.py
- symbolic_preview.py       <- app/preview_implementations/symbolic_preview.py

Depends on the ``slr_parsing`` package, plus sympy and latex2sympy2.

Submodules are importable directly (e.g.
``from expression_parsing.expression_utilities import parse_expression``); the
most commonly used names are also re-exported here for convenience.
"""

from .feedback import FeedbackTag

from .expression_utilities import (
    default_parameters,
    parse_expression,
    create_sympy_parsing_params,
    preprocess_expression,
    substitute,
    substitute_input_symbols,
    create_expression_set,
    convert_absolute_notation,
    sympy_to_latex,
    sympy_symbols,
    extract_latex,
    find_matching_parenthesis,
    compute_relative_tolerance_from_significant_decimals,
    SymbolDict,
)
from .syntactical_comparison import (
    patterns,
    is_number,
    is_number_regex,
    generate_arbitrary_number_pattern_matcher,
)
from .preview_utilities import (
    Params,
    Preview,
    Result,
    parse_latex,
    sanitise_latex,
)
from .symbolic_preview import (
    preview_function,
    parse_symbolic,
)

__all__ = [
    "FeedbackTag",
    "default_parameters",
    "parse_expression",
    "create_sympy_parsing_params",
    "preprocess_expression",
    "substitute",
    "substitute_input_symbols",
    "create_expression_set",
    "convert_absolute_notation",
    "sympy_to_latex",
    "sympy_symbols",
    "extract_latex",
    "find_matching_parenthesis",
    "compute_relative_tolerance_from_significant_decimals",
    "SymbolDict",
    "patterns",
    "is_number",
    "is_number_regex",
    "generate_arbitrary_number_pattern_matcher",
    "Params",
    "Preview",
    "Result",
    "parse_latex",
    "sanitise_latex",
    "preview_function",
    "parse_symbolic",
]
