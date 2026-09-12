# Changelog: compareexpressions-units

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.units` (was `units`).

### Fixed

- `litre`'s plural forms were the single string `'litres,liters'`, so neither plural was recognised. In natural (and legacy) mode `2 litres` parsed as **2 litre·second**, with the trailing `s` read as seconds. It now parses as 2 litre.
