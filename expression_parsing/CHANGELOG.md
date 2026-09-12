# Changelog: compareexpressions-expression-parsing

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.expression_parsing` (was `expression_parsing`).

### Security

- **`symbol_assumptions` is no longer evaluated as code.** The parameter string (e.g. `"('a','positive') ('f','function')"`) was passed to `eval()`, and each assumption was pasted into another `eval("Symbol('x', <assumption>=True)")`, so a task author (or anyone who could set evaluation parameters) could run arbitrary Python. Groups are now read with `ast.literal_eval` and must be pairs of strings; assumption names must be identifiers and are passed as `Symbol(name, **{assumption: True})`. Malformed input raises `SymbolAssumptionError` (a `ValueError`). Valid assumptions behave as before, including `constant` and `function`.

### Fixed

- Inputs such as `2E` or `xE` parse (fixed in `slr_parsing`: the implicit-multiplication convention parser scanned a capital `E` as its grammar symbol).
- `parse_expression("a=b=c")` raises `ExpressionParsingError` instead of silently returning `Eq(a, b)` (everything after the second `=` was dropped).
- With `strict_syntax`, arithmetic on `{}` set literals (e.g. `{x+1}*{x-1}`) raises `ExpressionParsingError`. It used to build `Mul(FiniteSet, FiniteSet)`, which SymPy deprecates (the `SymPyDeprecationWarning` noted in `NOTES.md`) and will reject in a future version.
- `create_sympy_parsing_params` fills in missing parameters from the defaults instead of raising `KeyError` (e.g. for `complexNumbers`) when the caller hasn't merged `default_parameters` first.
