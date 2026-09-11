# Phase 0: Repo scaffolding

Applies to all packages. No behaviour changes.

## Layout

- [ ] Move each package to `src/` layout under the namespace: `slr_parsing/slr_parsing/*.py` → `slr_parsing/src/compareexpressions/slr_parsing/*.py`, and likewise for `criteria`, `expression_parsing` and `units`.
- [ ] Add `py.typed` to each package. Don't add `compareexpressions/__init__.py`, since the PEP 420 namespace depends on its absence.
- [ ] Update test imports to `compareexpressions.<pkg>`, and confirm the carried-over tests still pass in the same numbers.

## Packaging (Poetry)

- [ ] Per-package `pyproject.toml`: PEP 621 `[project]`, build backend `poetry-core>=2`, `[tool.poetry] packages = [{ include = "compareexpressions", from = "src" }]`, `requires-python = ">=3.11"`.
- [ ] Sibling deps by name in `[project.dependencies]`, enriched in `[tool.poetry.dependencies]` with `{ path = "../<pkg>", develop = true }`.
- [ ] `poetry build` each package and check that the wheel `METADATA` has no path references. If it does, fall back to version constraints per package and path deps only in the root project.
- [ ] Root `pyproject.toml` with `package-mode = false`. The dev group holds the 4 packages as path/develop deps plus `pytest`, `pytest-cov`, `ruff` and `mypy`.
- [ ] `lf_toolkit` git dependency pinned to `ae52fa6` (added where first needed, in Phase 2).

## Tooling

- [ ] ruff (root): `target-version = "py311"`, line length 120, rules `E,F,W,I,UP,B,SIM,RUF,N`.
- [ ] mypy (root): `strict` for `slr_parsing` and `criteria`; `check_untyped_defs` and `disallow_untyped_defs` for `expression_parsing` and `units`. `ignore_missing_imports` for `latex2sympy2`, and overrides for untyped sympy internals.
- [ ] pytest: `filterwarnings = error::SyntaxWarning`, and `error::DeprecationWarning` scoped to our modules.
- [ ] `.github/workflows/ci.yml`: matrix Python 3.11/3.12/3.13. `pipx install poetry` → `poetry install` → `ruff check` → `ruff format --check` → `mypy` → `pytest` per package.

## Docs

- [ ] Rewrite `README.md`: Poetry install, new import paths, dependency graph without `evaluation_result`.
- [ ] Add a "Refactor" section to `NOTES.md` summarising the decisions in [README.md](README.md).
- [ ] Save the parity snapshot (see [README.md § Verification](README.md#verification)).
