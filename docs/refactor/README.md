# Refactor & tidy-up

This is the second stage after the extraction described in [`NOTES.md`](../../NOTES.md). The extraction was a faithful copy of the original code. This stage reshapes the packages before compareExpressions adopts them.

Each package has a checklist, and commits tick off items as they land:

| Order | Checklist | Package |
|---|---|---|
| 0 | [scaffolding.md](scaffolding.md) | Repo layout, Poetry, ruff, mypy, CI |
| 1 | [slr_parsing.md](slr_parsing.md) | `compareexpressions.slr_parsing` |
| 2 | [criteria.md](criteria.md) | `compareexpressions.criteria` (and retiring `evaluation_result`) |
| 3 | [expression_parsing.md](expression_parsing.md) | `compareexpressions.expression_parsing` |
| 4 | [units.md](units.md) | `compareexpressions.units` |

Baseline before the refactor: **468 tests pass** (10 slr_parsing, 7 evaluation_result, 10 criteria, 157 expression_parsing, 284 units).

## Agreed decisions

| Topic | Decision |
|---|---|
| Public API | Break freely: PEP 8 names and cleaner signatures. Each package gets a `CHANGELOG.md` with an old→new migration table. Version goes to `0.2.0`. |
| Bugs | Fix each one in its own commit, with a regression test that fails first. Behaviour changes go in the changelog. |
| Structure | Split large modules; typed data (NamedTuple/dataclass/Enum); a per-package exception hierarchy; a typed params dataclass in place of free-form `params` dicts. |
| Tooling | Poetry, ruff (lint + format), mypy, GitHub Actions CI. Python floor **3.11**, which lf_toolkit requires. |
| Import names | PEP 420 namespace: `compareexpressions.slr_parsing`, `.criteria`, `.expression_parsing`, `.units`. Distribution names stay `compareexpressions-<pkg>`. |
| Layout | `src/` layout per package, plus a root non-package Poetry project (`package-mode = false`) that path-installs every package into one dev venv. |
| evaluation_result | **Retired.** Generic result handling moves to `lf_toolkit.evaluation.Result`; criteria-specific helpers move into `criteria`. |
| lf_toolkit | Runtime dependency of `expression_parsing`, `units` and `criteria` for `Params`/`SymbolDict`/`Preview`/`Result`. It is not on PyPI, so it's a git dependency pinned to `lambda-feedback/toolkit-python@ae52fa6`. We install its core only, without the `parsing` extra, which pins a different latex2sympy fork. |
| FeedbackTag | Stays in `expression_parsing` as a frozen dataclass plus a `StrEnum` of tag names. Consumers resolve tags to strings before `Result.add_feedback(tag, str)`. |

## Working conventions

- Branch `refactor/package-tidy`, one commit per checklist item.
- Package order follows the dependency graph: slr_parsing → criteria → expression_parsing → units.
- Within a package: (1) move the layout with no code changes, tests green; (2) regression test and fix for each bug; (3) restructure without changing behaviour; (4) rename the API and write the migration table; (5) types and mypy; (6) ruff.
- Carry over the SymPy-heavy tests with only their imports and call shapes changed, so they act as a parity check.

## Verification

- [ ] Before Phase 1: save a JSON snapshot of outputs on `main` for every carried-over test input (`parse_expression` str/latex, both `preview_function`s, quantity value/unit/standard forms).
- [ ] After each package: diff against the snapshot. The only allowed differences are listed bug fixes, each noted in the changelog.
- [ ] `ruff check`, `ruff format --check`, `mypy` and `pytest` pass for all packages on 3.11, 3.12 and 3.13.
- [ ] No `SyntaxWarning`s; no `print(` or `eval(` left in `src/`.
- [ ] Adoption smoke test: `parse_quantity("2 kg m/s^2", QuantityParams.from_dict({...}))` → `2 | kilogram metre/second^2`, and both `preview_function`s return a valid `lf_toolkit.preview.Result`.

## Risks / open items

- **lf_toolkit is git-only**, so these packages can't go on PyPI until it is published. Importing `lf_toolkit.shared` also pulls in its server stack (anyio, ujson, jsonrpcserver) through `lf_toolkit/__init__.py`. Worth raising upstream.
- **Parity with compareExpressions:** several bug fixes change results for some inputs. The changelogs list each one so adoption can re-run compareExpressions' 3128-test suite with them in mind.
- **Poetry path-dependency enrichment** in PEP 621 mode needs checking in Phase 0. The fallback is Poetry-native dependencies per package, with path dependencies only in the root dev project.
