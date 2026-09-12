"""Regression tests for bugs carried over from the v0.1 extraction."""

from copy import deepcopy

import pytest

from compareexpressions.units import QuantityParseError, fix_exponents, parse_quantity, preview_function

NATURAL = {"strictness": "natural", "units_string": "SI common imperial"}


def parse(expr, params=NATURAL):
    return parse_quantity(expr, params)


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

    def test_unit_between_value_parts_raises_instead_of_recursing_forever(self):
        # v0.1 rotated left and right alternately until RecursionError.
        with pytest.raises(QuantityParseError, match="Cannot separate the value from the unit"):
            parse("5 m/s x")


class TestPreview:
    @pytest.mark.parametrize(
        ("latex", "expected"),
        [
            ("m^{-2}", "m**(-2)"),
            ("x^{23}", "x**(23)"),
            # With '**' the notation used to be skipped twice, eating the exponent's first character.
            ("m**{-2}", "m**(-2)"),
            ("x**{23}", "x**(23)"),
            ("x^2", "x**2"),
            # An unbraced exponent used to borrow the next brace anywhere in the string.
            ("x^2y^{3}", "x**2y**(3)"),
        ],
    )
    def test_fix_exponents(self, latex, expected):
        assert fix_exponents(latex) == expected

    def test_latex_preview_keeps_the_exponent_sign(self):
        preview = preview_function(r"162 \mathrm{~N} \mathrm{~m}**{-2}", {"is_latex": True})["preview"]
        assert preview["sympy"] == "162 newton metre**(-2)"

    def test_latex_preview_of_a_unit_alone(self):
        assert preview_function(r"\mathrm{kg}", {"is_latex": True})["preview"]["sympy"] == "kilogram"

    def test_preview_does_not_mutate_params(self):
        # Fixed while porting units to the typed expression_parsing API
        # (the LaTeX branch set params["is_latex"] = False on the caller's dict).
        params = {"is_latex": True, "symbols": {"F": {"latex": "F", "aliases": []}}}
        before = deepcopy(params)
        preview_function(r"3 \mathrm{kg}", params)
        assert params == before
