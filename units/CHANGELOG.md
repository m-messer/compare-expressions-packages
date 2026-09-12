# Changelog: compareexpressions-units

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.units` (was `units`).

### Fixed

- `litre`'s plural forms were the single string `'litres,liters'`, so neither plural was recognised. In natural (and legacy) mode `2 litres` parsed as **2 litre·second**, with the trailing `s` read as seconds. It now parses as 2 litre.
- A bracketed value and unit followed by another unit, such as `(2 m) s` or `(2 kg) (m/s)`, no longer crashes with `IndexError` in every strictness mode. Splitting value from unit rotated the tree into the group, which only works for binary nodes: for a group it made the root and the group each other's child. Groups are now kept whole, so these read the way `(2 m)` alone already did, with the whole input as the unit and the number as a factor of it. A clear error might serve learners better; this is only a first step.
- LaTeX exponents written `**{...}` lost their first character: `fix_exponents` skipped the operator twice, so `m**{-2}` became `m**(2)` and the preview turned N·m⁻² into N·m². An unbraced exponent also borrowed the next brace anywhere in the string (`x^2y^{3}` → `x**(y^{3)`). Only a brace directly after the operator is unwrapped now.
