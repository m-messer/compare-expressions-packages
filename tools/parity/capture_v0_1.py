"""Capture a parity baseline from the v0.1 (extracted, pre-refactor) API.

Run from the repo root at the pre-refactor commit, with the flat v0.1 package
directories on ``sys.path`` (this script arranges that itself):

    python tools/parity/capture_v0_1.py tools/parity/baseline.json

Every probe gets fresh parameters so that in-place mutation bugs in v0.1 do not
leak between probes. Errors are recorded as ``"ERROR"`` only (exception types
and messages are expected to change in the refactor).

The refactored packages are compared against this file by ``check.py``, which
builds the same keys through the new API. The only differences allowed are the
bug fixes listed in ``expected_changes.json``.
"""

import contextlib
import io
import json
import sys
import warnings
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for pkg in ("slr_parsing", "criteria", "expression_parsing", "units"):
    sys.path.insert(0, str(ROOT / pkg))

warnings.simplefilter("ignore")

from corpus import (  # noqa: E402
    CRITERIA_STRINGS,
    EXPRESSION_INPUTS,
    EXPRESSION_VARIANTS,
    LATEX_INPUTS,
    QUANTITY_INPUTS,
    QUANTITY_LATEX_INPUTS,
    QUANTITY_VARIANTS,
)

from criteria import generate_criteria_parser  # noqa: E402
from criteria.parsing import base_token_list  # noqa: E402
from expression_parsing import (  # noqa: E402
    create_sympy_parsing_params,
    default_parameters,
    parse_expression,
    sympy_to_latex,
)
from expression_parsing import preview_function as symbolic_preview  # noqa: E402
from units import SLR_quantity_parser, SLR_quantity_parsing, preview_function as quantity_preview  # noqa: E402

ERROR = "ERROR"


def probe(fn):
    # v0.1 prints from inside parse_latex; keep that out of the output.
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            return fn()
        except Exception:
            return ERROR


def expression_params(variant):
    params = deepcopy(default_parameters)
    params.update(deepcopy(EXPRESSION_VARIANTS[variant]))
    return params


def capture_expressions(out):
    for variant in EXPRESSION_VARIANTS:
        for expr in EXPRESSION_INPUTS:
            def parse():
                params = expression_params(variant)
                parsed = parse_expression(expr, create_sympy_parsing_params(params))
                if isinstance(parsed, set):
                    return {"parsed": sorted(str(p) for p in parsed)}
                return {"parsed": str(parsed), "latex": sympy_to_latex(parsed, params.get("symbols", {}))}

            out[f"expr.parse|{variant}|{expr}"] = probe(parse)
            out[f"expr.preview|{variant}|{expr}"] = probe(
                lambda: dict(symbolic_preview(expr, expression_params(variant))["preview"])
            )
    for variant in ("default", "symbols"):
        for expr in LATEX_INPUTS:
            def preview_latex():
                params = expression_params(variant)
                params["is_latex"] = True
                return dict(symbolic_preview(expr, params)["preview"])

            out[f"expr.preview_latex|{variant}|{expr}"] = probe(preview_latex)


def quantity_params(variant):
    params = deepcopy(default_parameters)
    params.update({"physical_quantity": True, "strictness": "natural", "units_string": "SI common imperial"})
    params.update(deepcopy(QUANTITY_VARIANTS[variant]))
    return params


def quantity_summary(q):
    def s(x):
        return None if x is None else str(x)

    return {
        "value": None if q.value is None else q.value.original_string(),
        "unit": None if q.unit is None else q.unit.original_string(),
        "content": q.ast_root.content_string(),
        "value_latex": q.value_latex_string,
        "unit_latex": q.unit_latex_string,
        "latex": q.latex_string,
        "standard_value": s(q.standard_value),
        "standard_unit": s(q.standard_unit),
        "expanded_unit": s(q.expanded_unit),
        "dimension": s(q.dimension),
        "unit_factor": s(q.converted_unit_factor),
        "messages": [[tag, fb.tag, dict(fb.inputs)] for tag, fb in q.messages],
    }


def capture_quantities(out):
    for variant in QUANTITY_VARIANTS:
        for expr in QUANTITY_INPUTS:
            def parse():
                params = quantity_params(variant)
                parser = SLR_quantity_parser(params)
                return quantity_summary(SLR_quantity_parsing(expr, params, parser, "response"))

            out[f"quantity.parse|{variant}|{expr}"] = probe(parse)
            out[f"quantity.preview|{variant}|{expr}"] = probe(
                lambda: dict(quantity_preview(expr, quantity_params(variant))["preview"])
            )
    for expr in QUANTITY_LATEX_INPUTS:
        def preview_latex():
            params = quantity_params("natural")
            params["is_latex"] = True
            return dict(quantity_preview(expr, params)["preview"])

        out[f"quantity.preview_latex|natural|{expr}"] = probe(preview_latex)


def capture_criteria(out):
    reserved = {"learner": {"response": "a*b*c"}, "task": {"answer": "c*b*a"}}
    for criterion in CRITERIA_STRINGS:
        def parse():
            # Pass a copy: v0.1 appends to (and sorts) the module-level default token list.
            parser = generate_criteria_parser(deepcopy(reserved), token_list=list(base_token_list))
            return parser.parse(parser.scan(criterion))[0].tree_string()

        out[f"criteria.parse|{criterion}"] = probe(parse)


def main():
    out = {}
    capture_criteria(out)
    capture_expressions(out)
    capture_quantities(out)
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
