# Phase 3: `compareexpressions.expression_parsing`

Depends on `slr_parsing`, `lf_toolkit`, `sympy` and `latex2sympy2` (lambda-feedback fork). The source is currently `expression_utilities.py` (868), `preview_utilities.py` (245), `symbolic_preview.py` (133), `syntactical_comparison.py` (100) and `feedback.py`.

## Target modules

| Module | Contents |
|---|---|
| `params.py` | Frozen `ExpressionParams` dataclass with `from_dict(Mapping)`: maps JSON keys (`complexNumbers`, `specialFunctions`), ignores unrelated keys, and normalises symbols once (drops empty codes/aliases, moves `lambda`→`lamda`). Also `SympyParsingConfig` with `from_params(params, unsplittable_symbols=(), symbol_assumptions=())`. |
| `symbol_tables.py` | `ELEMENTARY_FUNCTIONS`, `GREEK_SYMBOLS` as tuples of `SymbolAliases(name, aliases)`; upper-case aliases built by a function, not by mutating lists at import time |
| `preprocessing.py` | `create_expression_set`, `is_multiple_answers_wrapper`, `convert_bracket_notation`, `has_matching_brackets`, `find_matching_parenthesis`, `convert_absolute_notation`, `convert_unicode_dashes`, `preprocess_expression` (returns a result dataclass) |
| `substitution.py` | `substitute`, `substitutions_sort_key`, pure `substitute_input_symbols`, greek/elementary protection substitutions |
| `conventions.py` | Implicit-multiplication convention parser, cached per convention (`functools.cache`) |
| `sympy_parsing.py` | `parse_expression`, `sympy_symbols`, transformation selection. The private SymPy `_token_splittable` import is isolated here. |
| `latex.py` | `LatexPrinter` subclass, `sympy_to_latex`, `latex_symbols`, `extract_latex`, `parse_latex`, `E`/`e` placeholder handling, `sanitise_latex` |
| `preview.py` | `parse_symbolic`, `preview_function` → `lf_toolkit.preview.Result` |
| `numbers.py` | Raw-string number regexes, `is_number`, complex-form checks, `generate_arbitrary_number_pattern_matcher`, `compute_relative_tolerance_from_significant_decimals`, and a `SyntacticalPattern` dataclass replacing the `patterns` dict |
| `feedback.py` | Frozen `FeedbackTag(tag, inputs)` dataclass and `FeedbackTagName` `StrEnum` |
| `errors.py` | `ExpressionParsingError(ValueError)` → `ExpressionSyntaxError` (carries a `FeedbackTag`), `LatexParseError`, `SymbolAssumptionError` |

## Checklist

### Bugs (regression test first, one commit each)

- [ ] **Security:** `symbol_assumptions` goes through `eval()` on author-supplied strings, and so does `eval("Symbol('"+s+"',"+a+"=True)")`. Replace with `ast.literal_eval` and `Symbol(name, **{assumption: True})`, validating against SymPy's known assumptions. Make the `constant` branch explicit (SymPy accepts `constant=True`, so keep that behaviour).
- [ ] `parse_expression("2E")` / `("xE")` crash in the convention parser. The root cause is fixed in slr_parsing; this adds the end-to-end test.
- [ ] `substitute_input_symbols` mutates `params["symbols"]`. On the second call a user-defined `lambda` symbol is overwritten by the default: its aliases become `['lambda', 'lambda']` and the custom alias is lost.
- [ ] Empty-alias removal deletes by ascending index, so indices shift, and the `.strip()` results are discarded: `["", "", "xx"]` leaves `['']`. The legacy `input_symbols` path has the same problem.
- [ ] `create_expression_set("plus_minus")` → `IndexError`.
- [ ] `parse_expression("a=b=c")` silently returns `Eq(a, b)`. Raise `ExpressionParsingError`.
- [ ] `preview_function` / `parse_latex` mutate the caller's params, and `sympy_to_latex` mutates its `settings` argument.
- [ ] `create_sympy_parsing_params` raises `KeyError` unless defaults were merged first.
- [ ] `parse_latex`: `print(e)` swallows alias errors; `ValueError("…: ", str(e))` has a tuple payload and a "pass" typo; `"\pm"` is an invalid escape.
- [ ] Fix the SymPy `Mul` deprecation warnings (non-`Expr` args) at their source.

### Restructure (no behaviour change)

- [ ] Split the four modules into the target modules above.
- [ ] Replace `default_parameters` and `parsing_params` dicts with `ExpressionParams` / `SympyParsingConfig`.
- [ ] Use `lf_toolkit.shared.Params`/`SymbolDict` and `lf_toolkit.preview.Preview`/`Result`, and delete the local TypedDicts.
- [ ] Cache the convention parser (the SLR tables are rebuilt on every `parse_expression` call today).
- [ ] Remove the dead `printing_symbols`, the unused imports, the `atol`/`rtol` updates inside the loop, and the template docstrings.
- [ ] Document why `escape_regex_reserved_characters` isn't `re.escape` (it would escape spaces that are stripped afterwards).

### API (break freely, recorded in `CHANGELOG.md`)

- [ ] `create_sympy_parsing_params(params, ...)` → `SympyParsingConfig.from_params(...)`
- [ ] `default_parameters` dict → `ExpressionParams` defaults
- [ ] `preprocess_expression` returns a result dataclass instead of `(success, expr, feedback)`
- [ ] `raise SyntaxError(FeedbackTag(...))` → `ExpressionSyntaxError(feedback_tag)`
- [ ] `FeedbackTag` namedtuple → frozen dataclass; tag names as `FeedbackTagName`
- [ ] `patterns` dict → `SyntacticalPattern` instances

### Dependencies

- [ ] Pin `latex2sympy2` to the lambda-feedback fork (what compareExpressions uses) instead of PyPI 1.8.3, and confirm the 157 carried-over tests pass on it.
- [ ] Add `lf_toolkit` (git, `ae52fa6`, core only).

### Types & lint

- [ ] `disallow_untyped_defs` + `check_untyped_defs` mypy clean; `ruff` clean; no `SyntaxWarning`.
