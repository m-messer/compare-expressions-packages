# Phase 4: `compareexpressions.units`

Depends on `slr_parsing`, `expression_parsing`, `lf_toolkit` and `sympy`. The source is currently `physical_quantity_utilities.py` (602), `physical_quantity_preview.py` (128) and `unit_system_conversions.py` (145).

## Target modules

| Module | Contents |
|---|---|
| `data.py` | NamedTuples `Prefix(name, symbol, factor, alternatives)`, `BaseUnit(name, symbol, dimension, alternatives, plurals)`, `Unit(name, symbol, si_expansion, alternatives, plurals)`. Constants `SI_PREFIXES`, `SI_BASE_UNITS`, `SI_DERIVED_UNITS`, `VERY_COMMON_UNITS`, `COMMON_UNITS`, `IMPERIAL_UNITS`, `UNIT_SETS`. `CONVERSION_TO_BASE_SI` is built by a function. |
| `params.py` | `QuantityParams(ExpressionParams)`: `strictness: Literal["strict", "natural"]` (`legacy` normalised once, with a `legacy_preprocessing` flag) and `unit_sets: frozenset[str]` parsed from `units_string` |
| `tags.py` | `QuantityTag` Enum with readable names (`UNIT`, `NON_UNIT`, `NUMBER`, and `R` named after checking its usage) |
| `parser.py` | Unit dictionaries, `starts_with_unit` / `starts_with_number`, tag handler, error handlers, cached `build_quantity_parser(unit_sets, strictness)` |
| `quantity.py` | `parse_quantity(expr, params, name) -> PhysicalQuantity`. `PhysicalQuantity` becomes a result dataclass; the rotate/split, revert, latex and standard-form logic move into focused functions. Forms stay eager. |
| `preprocessing.py` | `preprocess_quantity(expr, params) -> str`, `preprocess_legacy` (patterns compiled once), `transform_prefixes_to_standard` |
| `preview.py` | `preview_function`, `fix_exponents` |
| `errors.py` | `QuantityError` → `QuantityParseError`, `UnitConversionError` |

## Checklist

### Bugs (regression test first, one commit each)

- [ ] Litre's plurals are written as `('litres,liters',)`, one string, so in natural/legacy mode `"2 litres"` parses as `2 | litre second`.
- [ ] `"(2 m) s"` raises `IndexError` in every strictness mode (`_rotate` → `tag_handler`). Investigate the single-child rotate path, and `node.label in "SPACE"`, which is a substring test that should be `==`. It should either parse or raise `QuantityParseError`.
- [ ] `fix_exponents` skips `len(notation)` twice, so `m**{-2}` → `m**(2)` (the sign is lost) and `x**{23}` → `x**(3)`.
- [ ] Parser strictness defaults to `"natural"` but the tag handler defaults to `"strict"`, and `"legacy"` isn't normalised for the tag handler. This is latent (no output difference on a 14-input sample); `QuantityParams` becomes the single source.
- [ ] `max_unit_name_length` measures the number of dict keys, not the longest name, so the strict matcher over-iterates. Perf only.
- [ ] `preview_function` passes raw `params` to `parse_expression` and mutates `params["is_latex"]`.

### Restructure (no behaviour change)

- [ ] `unit_system_conversions.py` → `data.py` with NamedTuples, and remove every positional `x[0]..x[4]` index.
- [ ] Split `physical_quantity_utilities.py` into `tags.py` / `parser.py` / `quantity.py` / `preprocessing.py`.
- [ ] Cache the quantity parser per `(unit_sets, strictness)`; `preview_function` rebuilds it on every call today.
- [ ] Compute valid units in one helper. `__init__` and `_value_latex` currently build two different sets (names only, versus names + symbols + alternatives + plurals); keep both variants but give them names.
- [ ] Remove the module-level `temp_dict`, the identity-lambda `tag_handler` default and the `CONSIDER` comment.
- [ ] Bare `Exception` → `QuantityParseError` / `UnitConversionError`.

### API (break freely, recorded in `CHANGELOG.md`)

- [ ] `set_of_*` → upper-case NamedTuple constants; `units_sets_dictionary` → `UNIT_SETS`
- [ ] `QuantityTags` (U/V/N/R) → `QuantityTag` with descriptive names
- [ ] `SLR_quantity_parser(params)` → `build_quantity_parser(unit_sets, strictness)`
- [ ] `SLR_quantity_parsing(expr, params, parser, name)` → `parse_quantity(expr, params, name)`
- [ ] `expression_preprocess` → `preprocess_quantity` (returns `str`, not `(True, expr, None)`)
- [ ] `PhysicalQuantity.messages` keep `FeedbackTag` payloads (now the dataclass)

### Types & lint

- [ ] `disallow_untyped_defs` + `check_untyped_defs` mypy clean; `ruff` clean.
