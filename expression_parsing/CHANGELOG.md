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
- `create_expression_set` no longer raises `IndexError` when an expression is only `plus_minus` (± with nothing after it).
- A user-defined `lambda` symbol keeps its LaTeX and aliases. `substitute_input_symbols` renames `lambda` to `lamda` inside `params["symbols"]`, and a second call (the preview makes several) replaced the renamed symbol with the default one, so previews showed `\lambda` instead of the task's LaTeX and custom aliases stopped working.
- Symbol aliases are stripped and blank aliases dropped as intended. The `.strip()` result was discarded, and blank aliases were deleted by index while the list shrank, which removed real aliases (e.g. `["", "", "xx"]` lost `"xx"`). The same cleanup for the legacy `input_symbols` format is fixed too; it could raise `IndexError` on an empty entry.
- `preview_function` and `parse_latex` no longer modify the caller's parameters (they merged in defaults, set `rationalise`, and normalised `symbols` in place), and `sympy_to_latex` no longer adds its default settings to the caller's `settings` dict.
- `parse_latex` no longer prints alias parse errors to stdout (an alias that isn't an expression is still used as a plain symbol name), and raises `LatexParseError` (a `ValueError`) with a single message. It used to raise `ValueError("Failed to pass expression during preview: ", str(e))`, whose message was a tuple.
- `sanitise_latex` raises `LatexParseError` for an unclosed `\mathrm{` / `\text{` instead of looping forever (the scan restarted from the beginning). units' LaTeX preview runs it on learner input, so a malformed response would hang the evaluation.
