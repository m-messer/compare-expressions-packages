# Changelog: compareexpressions-units

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.units` (was `units`).

### Renamed and restructured

Parameters are typed now. `QuantityParams` extends `expression_parsing.ExpressionParams` with `strictness`, `legacy_preprocessing` and `unit_sets`, and `QuantityParams.from_dict(evaluation_params)` maps `strictness: "legacy"` and `units_string`. Parsers are built once per `(unit_sets, strictness)` and cached.

| v0.1 | 0.2.0 |
|---|---|
| `units` (import) | `compareexpressions.units` |
| `SLR_quantity_parser(params)` + `SLR_quantity_parsing(expr, params, parser, name)` | `parse_quantity(expr, params, name="response")` (parser cached internally; `build_quantity_parser(unit_sets, strictness)` if you need it) |
| `PhysicalQuantity(name, parameters, ast_root, parser, messages, tag_handler)` | created by `parse_quantity` |
| `quantity.value_latex_string` / `unit_latex_string` / `latex_string` | `quantity.value_latex` / `unit_latex` / `latex` |
| `quantity.converted_unit_factor` | `quantity.unit_factor` |
| `quantity.parsing_params` (dict) | `quantity.parsing_config` (`SympyParsingConfig`) |
| `quantity.parameters` (dict) | `quantity.params` (`QuantityParams`) |
| `expression_preprocess(name, expr, params)` → `(True, expr, None)` | `preprocess_quantity(name, expr, params)` → `Preprocessed` (same shape as `expression_parsing.preprocess_expression`) |
| `params["strictness"] == "legacy"` | `QuantityParams(strictness="natural", legacy_preprocessing=True)`; `from_dict` maps `"legacy"` |
| `params["units_string"]` (substring test) | `QuantityParams.unit_sets` (frozenset); `from_dict` maps `units_string` the same way |
| `QuantityTags.U` / `V` / `N` / `R` | `QuantityTag.UNIT` / `NON_UNIT` / `NUMBER` / `REJECTED_UNIT` |
| `set_of_SI_prefixes` / `set_of_SI_base_unit_dimensions` / `set_of_derived_SI_units_in_SI_base_units` / `set_of_very_common_units_in_SI` / `set_of_common_units_in_SI` / `set_of_imperial_units` (sets of positional tuples) | `SI_PREFIXES` / `SI_BASE_UNITS` / `SI_DERIVED_UNITS` / `VERY_COMMON_UNITS` / `COMMON_UNITS` / `IMPERIAL_UNITS`: ordered tuples of `Prefix(name, symbol, factor, alternatives)`, `BaseUnit(name, symbol, dimension, alternatives, plurals)` and `Unit(name, symbol, si_expansion, alternatives, plurals)` |
| `units_sets_dictionary` | `UNIT_SETS`; `units_in(unit_sets)` |
| `conversion_to_base_si_units` | `CONVERSION_TO_BASE_SI` |
| `preview_function(response, params)` mutated `params` | takes `QuantityParams` or a mapping; never mutates it |
| bare `Exception`s | `QuantityParseError` / `UnitConversionError` (both `QuantityError`, a `ValueError`) |

Modules: `data` (was `unit_system_conversions`), `params`, `tags`, `parser`, `quantity`, `preprocessing`, `preview`, `errors` (replacing `physical_quantity_utilities` and `physical_quantity_preview`).

### Fixed

- `litre`'s plural forms were the single string `'litres,liters'`, so neither plural was recognised. In natural (and legacy) mode `2 litres` parsed as **2 litre·second**, with the trailing `s` read as seconds. It now parses as 2 litre.
- A bracketed value and unit followed by another unit, such as `(2 m) s` or `(2 kg) (m/s)`, no longer crashes with `IndexError` in every strictness mode. Splitting value from unit rotated the tree into the group, which only works for binary nodes: for a group it made the root and the group each other's child. Groups are now kept whole, so these read the way `(2 m)` alone already did, with the whole input as the unit and the number as a factor of it. A clear error might serve learners better; this is only a first step.
- LaTeX exponents written `**{...}` lost their first character: `fix_exponents` skipped the operator twice, so `m**{-2}` became `m**(2)` and the preview turned N·m⁻² into N·m². An unbraced exponent also borrowed the next brace anywhere in the string (`x^2y^{3}` → `x**(y^{3)`). Only a brace directly after the operator is unwrapped now.
- A unit between two value parts (e.g. `5 m/s x`) raises `QuantityParseError("Cannot separate the value from the unit ...")` instead of recursing until `RecursionError`. Splitting value from unit rotated the tree left and right alternately, each rotation undoing the last.
- Splitting value from unit re-tagged the tree with a tag handler for a different strictness than the parser's. It defaulted to strict when `strictness` was omitted (the parser defaulted to natural), and for `legacy` it matched neither mode. It now uses the parser's own rules. This changes legacy-mode `3 µs` (previously the whole input read as a unit with dimension `3*mu*time`; now read as a value, reporting `s` as a reverted unit, as natural mode's rules define. Neither reads microseconds: legacy preprocessing doesn't normalise `µ`).
- The strict unit matcher tried every length up to the *number* of known units (hundreds) at each position; it now stops at the longest unit spelling.
- The quantity preview previously passed the raw parameter dict to `parse_expression` as if it were parsing parameters; it now uses a proper parsing configuration (no output changes on the parity corpus).
- The LaTeX preview of a response that is only a unit gave SymPy output such as `Nonekilogram`: the missing value was printed as `None`. It is now just the unit.
