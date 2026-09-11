"""Test fixtures for the units package.

``default_parameters`` mirrors the physical-quantity context defaults defined in
compareExpressions (app/context/physical_quantity.py): the symbolic default
parameters from expression_parsing, extended with the quantity-specific keys.
Vendored here so the ported quantity tests do not depend on the app's core
evaluation layer.
"""

from copy import deepcopy

from expression_parsing import default_parameters as symbolic_default_parameters

default_parameters = deepcopy(symbolic_default_parameters)
default_parameters.update(
    {
        "physical_quantity": True,
        "strictness": "natural",
        "units_string": "SI common imperial",
    }
)
