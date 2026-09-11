"""Diff the current packages against the v0.1 parity baseline.

    poetry run python tools/parity/check.py            # report, exit 1 on unexpected diffs
    poetry run python tools/parity/check.py --update   # also record current values of
                                                       # already-listed expected changes

Probes mirror ``capture_v0_1.py`` key-for-key; only the calls into the
packages are adapted as their APIs change during the refactor. Intentional
behaviour changes (bug fixes) are listed in ``expected_changes.json`` as
``{key: {"reason": ..., "value": <new output>}}`` and must match exactly.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
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

from compareexpressions.criteria import generate_criteria_parser  # noqa: E402
from compareexpressions.criteria.parsing import base_token_list  # noqa: E402
from compareexpressions.expression_parsing import (  # noqa: E402
    create_sympy_parsing_params,
    default_parameters,
    parse_expression,
    sympy_to_latex,
)
from compareexpressions.expression_parsing import preview_function as symbolic_preview  # noqa: E402
from compareexpressions.units import SLR_quantity_parser, SLR_quantity_parsing  # noqa: E402
from compareexpressions.units import preview_function as quantity_preview  # noqa: E402

ERROR = "ERROR"


def probe(fn: Any, *args: Any) -> Any:
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            return fn(*args)
        except Exception:
            return ERROR


# --- Adapters: the only part that changes as the package APIs change. ---


def criteria_tree(criterion: str) -> str:
    reserved = {"learner": {"response": "a*b*c"}, "task": {"answer": "c*b*a"}}
    parser = generate_criteria_parser(reserved, token_list=list(base_token_list))
    return parser.parse(parser.scan(criterion))[0].tree_string()


def expression_params(variant: str) -> dict[str, Any]:
    params: dict[str, Any] = deepcopy(default_parameters)
    params.update(deepcopy(EXPRESSION_VARIANTS[variant]))
    return params


def expression_parse(expr: str, variant: str) -> dict[str, Any]:
    params = expression_params(variant)
    parsed = parse_expression(expr, create_sympy_parsing_params(params))
    if isinstance(parsed, set):
        return {"parsed": sorted(str(p) for p in parsed)}
    return {"parsed": str(parsed), "latex": sympy_to_latex(parsed, params.get("symbols", {}))}


def expression_preview(expr: str, variant: str, is_latex: bool) -> dict[str, Any]:
    params = expression_params(variant)
    if is_latex:
        params["is_latex"] = True
    return dict(symbolic_preview(expr, cast(Any, params))["preview"])


def quantity_params(variant: str) -> dict[str, Any]:
    params: dict[str, Any] = deepcopy(default_parameters)
    params.update({"physical_quantity": True, "strictness": "natural", "units_string": "SI common imperial"})
    params.update(deepcopy(QUANTITY_VARIANTS[variant]))
    return params


def quantity_parse(expr: str, variant: str) -> dict[str, Any]:
    params = quantity_params(variant)
    q = SLR_quantity_parsing(expr, params, SLR_quantity_parser(params), "response")

    def s(x: Any) -> str | None:
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


def quantity_preview_dict(expr: str, variant: str, is_latex: bool) -> dict[str, Any]:
    params = quantity_params(variant)
    if is_latex:
        params["is_latex"] = True
    return dict(quantity_preview(expr, cast(Any, params))["preview"])


# --- Probe layout: must stay key-for-key identical to capture_v0_1.py. ---


def collect() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for criterion in CRITERIA_STRINGS:
        out[f"criteria.parse|{criterion}"] = probe(criteria_tree, criterion)
    for variant in EXPRESSION_VARIANTS:
        for expr in EXPRESSION_INPUTS:
            out[f"expr.parse|{variant}|{expr}"] = probe(expression_parse, expr, variant)
            out[f"expr.preview|{variant}|{expr}"] = probe(expression_preview, expr, variant, False)
    for variant in ("default", "symbols"):
        for expr in LATEX_INPUTS:
            out[f"expr.preview_latex|{variant}|{expr}"] = probe(expression_preview, expr, variant, True)
    for variant in QUANTITY_VARIANTS:
        for expr in QUANTITY_INPUTS:
            out[f"quantity.parse|{variant}|{expr}"] = probe(quantity_parse, expr, variant)
            out[f"quantity.preview|{variant}|{expr}"] = probe(quantity_preview_dict, expr, variant, False)
    for expr in QUANTITY_LATEX_INPUTS:
        out[f"quantity.preview_latex|natural|{expr}"] = probe(quantity_preview_dict, expr, "natural", True)
    return out


def main() -> int:
    update = "--update" in sys.argv
    baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
    expected_path = HERE / "expected_changes.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    # Round-trip through JSON so tuples/lists compare the same way as the baseline.
    current = json.loads(json.dumps(collect(), ensure_ascii=False))

    if set(current) != set(baseline):
        print("Probe keys differ from baseline:", sorted(set(current) ^ set(baseline))[:10])
        return 1

    unexpected = [k for k in current if current[k] != baseline[k] and k not in expected]
    wrong = [k for k in expected if current[k] != expected[k]["value"]]

    for k in unexpected:
        print(f"UNEXPECTED {k}\n  baseline: {baseline[k]}\n  current:  {current[k]}")
    for k in wrong:
        print(f"MISMATCH (expected change) {k}\n  expected: {expected[k]['value']}\n  current:  {current[k]}")
        if update:
            expected[k]["value"] = current[k]

    if update and wrong:
        expected_path.write_text(json.dumps(expected, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        print(f"Updated {len(wrong)} expected value(s).")

    print(
        f"{len(current)} probes; {len(expected)} expected changes; "
        f"{len(unexpected)} unexpected; {len(wrong)} mismatched"
    )
    return 1 if unexpected or (wrong and not update) else 0


if __name__ == "__main__":
    sys.exit(main())
