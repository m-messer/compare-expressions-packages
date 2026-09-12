# Changelog: compareexpressions-expression-parsing

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.expression_parsing` (was `expression_parsing`).

### Security

- **`symbol_assumptions` is no longer evaluated as code.** The parameter string (e.g. `"('a','positive') ('f','function')"`) was passed to `eval()`, and each assumption was pasted into another `eval("Symbol('x', <assumption>=True)")`, so a task author (or anyone who could set evaluation parameters) could run arbitrary Python. Groups are now read with `ast.literal_eval` and must be pairs of strings; assumption names must be identifiers and are passed as `Symbol(name, **{assumption: True})`. Malformed input raises `SymbolAssumptionError` (a `ValueError`). Valid assumptions behave as before, including `constant` and `function`.

### Fixed

- Inputs such as `2E` or `xE` parse (fixed in `slr_parsing`: the implicit-multiplication convention parser scanned a capital `E` as its grammar symbol).
