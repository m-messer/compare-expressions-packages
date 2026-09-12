"""Regression tests for bugs carried over from the v0.1 extraction."""

from copy import deepcopy

import pytest

from compareexpressions.units import SLR_quantity_parser, SLR_quantity_parsing, preview_function
from compareexpressions.units.physical_quantity_preview import fix_exponents

NATURAL = {"strictness": "natural", "units_string": "SI common imperial"}


def parse(expr, params=NATURAL):
    return SLR_quantity_parsing(expr, params, SLR_quantity_parser(params), "response")


class TestUnitData:
    @pytest.mark.parametrize("plural", ["litres", "liters"])
    def test_litre_plurals(self, plural):
        quantity = parse(f"2 {plural}")
        assert quantity.unit.content_string() == "litre"


class TestParsing:
    @pytest.mark.parametrize("expr", ["(2 m) s", "(2 m) (s)", "(x m) s"])
    def test_grouped_quantity_followed_by_a_unit(self, expr):
        # Groups are atomic: as for "(2 m)" alone, the whole input is the unit.
        quantity = parse(expr)
        assert quantity.value is None
        assert quantity.unit.content_string() == quantity.ast_root.content_string()


class TestPreview:
    @pytest.mark.parametrize(
        ("latex", "expected"),
        [
            ("m^{-2}", "m**(-2)"),
            ("x^{23}", "x**(23)"),
            # With '**' the notation was skipped twice, eating the exponent's first character.
            pytest.param("m**{-2}", "m**(-2)", marks=pytest.mark.xfail(strict=True, reason="v0.1 bug")),
            pytest.param("x**{23}", "x**(23)", marks=pytest.mark.xfail(strict=True, reason="v0.1 bug")),
        ],
    )
    def test_fix_exponents(self, latex, expected):
        assert fix_exponents(latex) == expected

    def test_preview_does_not_mutate_params(self):
        # Fixed while porting units to the typed expression_parsing API
        # (the LaTeX branch set params["is_latex"] = False on the caller's dict).
        params = {"is_latex": True, "symbols": {"F": {"latex": "F", "aliases": []}}}
        before = deepcopy(params)
        preview_function(r"3 \mathrm{kg}", params)
        assert params == before
