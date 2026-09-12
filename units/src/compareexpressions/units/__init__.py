"""Physical quantities: unit data, parsing into value and unit, dimensional analysis, preview.

Typical use::

    params = QuantityParams.from_dict(evaluation_params)
    quantity = parse_quantity("9.81 m/s^2", params)
    quantity.value, quantity.unit, quantity.dimension, quantity.standard_value

or ``preview_function(response, evaluation_params)`` for a preview.

Extracted from compareExpressions; unit-like text read as part of a value is
reported as ``REVERTED_UNIT`` :class:`~compareexpressions.expression_parsing.FeedbackTag` messages.
"""

from .data import (
    ALL_UNITS,
    COMMON_UNITS,
    CONVERSION_TO_BASE_SI,
    IMPERIAL_UNITS,
    SI_BASE_UNITS,
    SI_DERIVED_UNITS,
    SI_PREFIXES,
    UNIT_SETS,
    VERY_COMMON_UNITS,
    BaseUnit,
    Prefix,
    Unit,
    units_in,
)
from .errors import QuantityError, QuantityParseError, UnitConversionError
from .params import QuantityParams, Strictness
from .parser import build_quantity_parser
from .preprocessing import preprocess_legacy, preprocess_quantity, transform_prefixes_to_standard
from .preview import fix_exponents, preview_function
from .quantity import REVERTED_UNIT, PhysicalQuantity, parse_quantity
from .tags import QuantityTag

__all__ = [
    "ALL_UNITS",
    "COMMON_UNITS",
    "CONVERSION_TO_BASE_SI",
    "IMPERIAL_UNITS",
    "REVERTED_UNIT",
    "SI_BASE_UNITS",
    "SI_DERIVED_UNITS",
    "SI_PREFIXES",
    "UNIT_SETS",
    "VERY_COMMON_UNITS",
    "BaseUnit",
    "PhysicalQuantity",
    "Prefix",
    "QuantityError",
    "QuantityParams",
    "QuantityParseError",
    "QuantityTag",
    "Strictness",
    "Unit",
    "UnitConversionError",
    "build_quantity_parser",
    "fix_exponents",
    "parse_quantity",
    "preprocess_legacy",
    "preprocess_quantity",
    "preview_function",
    "transform_prefixes_to_standard",
    "units_in",
]
