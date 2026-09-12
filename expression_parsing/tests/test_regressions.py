"""Regression tests for bugs carried over from the v0.1 extraction."""

import sys
import warnings
from copy import deepcopy

import pytest

from compareexpressions.expression_parsing import default_parameters
from compareexpressions.expression_parsing.expression_utilities import (
    create_expression_set,
    create_sympy_parsing_params,
    parse_expression,
    substitute_input_symbols,
)
from compareexpressions.expression_parsing.preview_utilities import parse_latex
from compareexpressions.expression_parsing.symbolic_preview import preview_function


def parsing_params(**overrides):
    params = deepcopy(default_parameters)
    params.update(overrides)
    return create_sympy_parsing_params(params)


class TestSymbolAssumptions:
    def test_assumption_tuples_are_not_executed(self):
        injected = "(__import__('sys').modules.__setitem__('pwned_by_assumptions', 1), 'positive')"
        with pytest.raises(ValueError):
            parsing_params(symbol_assumptions=injected)
        assert "pwned_by_assumptions" not in sys.modules

    def test_assumption_names_must_be_identifiers(self):
        with pytest.raises(ValueError, match="positive=True"):
            parsing_params(symbol_assumptions="('x', 'positive=True')")

    def test_valid_assumptions_still_apply(self):
        params = parsing_params(symbol_assumptions="('a','positive') ('f','function') ('c','constant')")
        assert params["symbol_dict"]["a"].is_positive
        assert params["symbol_dict"]["f"](1).func.__name__ == "f"
        assert "c" in params["constants"]


class TestParsing:
    def test_capital_e_after_implicit_multiplication(self):
        # Fixed in slr_parsing (the convention parser scanned "E" as a grammar symbol).
        assert str(parse_expression("2E", parsing_params())) == "2*E"
        assert str(parse_expression("xE", parsing_params())) == "E*x"

    def test_chained_equalities_are_rejected(self):
        with pytest.raises(ValueError, match="="):
            parse_expression("a=b=c", parsing_params())

    def test_arithmetic_on_sets_is_rejected_in_strict_syntax(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with pytest.raises(ValueError, match="set"):
                parse_expression("{x+1}*{x-1}", parsing_params(strict_syntax=True))

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: create_sympy_parsing_params needs pre-merged defaults")
    def test_parsing_params_default_missing_keys(self):
        assert create_sympy_parsing_params({})["complexNumbers"] is False

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: a lone plus_minus raises IndexError")
    def test_lone_plus_minus(self):
        assert sorted(create_expression_set("plus_minus", {})) == ["", "-"]


class TestInputSymbols:
    @pytest.mark.xfail(strict=True, reason="v0.1 bug: a second call overwrites a user-defined lambda symbol")
    def test_user_defined_lambda_survives_repeated_substitution(self):
        params = {"symbols": {"lambda": {"latex": r"\Lambda_0", "aliases": ["lam"]}}}
        assert substitute_input_symbols(["lam"], params) == ["lamda"]
        assert substitute_input_symbols(["lam"], params) == ["lamda"]

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: removing empty aliases shifts indices and drops real ones")
    def test_empty_aliases_do_not_remove_real_ones(self):
        params = {"symbols": {"x": {"latex": "x", "aliases": ["", "", "xx"]}}}
        assert substitute_input_symbols(["xx"], params) == ["x"]

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: aliases are never stripped (the .strip() result is discarded)")
    def test_aliases_are_stripped(self):
        params = {"symbols": {"x": {"latex": "x", "aliases": [" xx "]}}}
        assert substitute_input_symbols(["xx"], params) == ["x"]


class TestNoSideEffects:
    @pytest.mark.xfail(strict=True, reason="v0.1 bug: preview_function mutates the caller's params")
    def test_preview_does_not_mutate_params(self):
        params = {"symbols": {"x": {"latex": "x", "aliases": ["xx"]}}}
        before = deepcopy(params)
        preview_function("xx + 1", params)
        assert params == before

    @pytest.mark.xfail(strict=True, reason="v0.1 bug: parse_latex prints alias errors and raises a tuple message")
    def test_parse_latex_reports_errors_cleanly(self, capsys):
        parse_latex("x", {"x": {"latex": "x", "aliases": ["1+"]}}, False)
        assert capsys.readouterr().out == ""
        with pytest.raises(ValueError) as info:
            parse_latex(r"\frac{x", {}, False)
        assert len(info.value.args) == 1
