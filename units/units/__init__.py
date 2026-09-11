"""Unit system data, physical-quantity parsing and dimensional analysis.

Extracted from compareExpressions and decoupled from app-specific feedback
strings (reverted-unit messages now carry a
``expression_parsing.FeedbackTag``). Modules:
- unit_system_conversions.py    <- app/utility/unit_system_conversions.py (pure data)
- physical_quantity_utilities.py <- app/utility/physical_quantity_utilities.py
- physical_quantity_preview.py   <- app/preview_implementations/physical_quantity_preview.py

Depends on the ``slr_parsing`` and ``expression_parsing`` packages, plus sympy.
"""

from .unit_system_conversions import (
    set_of_SI_prefixes,
    set_of_SI_base_unit_dimensions,
    set_of_derived_SI_units_in_SI_base_units,
    set_of_very_common_units_in_SI,
    set_of_common_units_in_SI,
    set_of_imperial_units,
    conversion_to_base_si_units,
)
from .physical_quantity_utilities import (
    QuantityTags,
    PhysicalQuantity,
    units_sets_dictionary,
    SLR_quantity_parser,
    SLR_quantity_parsing,
    expression_preprocess,
)
from .physical_quantity_preview import preview_function

__all__ = [
    "set_of_SI_prefixes",
    "set_of_SI_base_unit_dimensions",
    "set_of_derived_SI_units_in_SI_base_units",
    "set_of_very_common_units_in_SI",
    "set_of_common_units_in_SI",
    "set_of_imperial_units",
    "conversion_to_base_si_units",
    "QuantityTags",
    "PhysicalQuantity",
    "units_sets_dictionary",
    "SLR_quantity_parser",
    "SLR_quantity_parsing",
    "expression_preprocess",
    "preview_function",
]
