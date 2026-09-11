# compareExpressions packages

Reusable packages extracted from the
[compareExpressions](https://github.com/lambda-feedback/compareExpressions)
evaluation function. Each package is independently installable and self-contained;
the app-specific *core evaluation* logic stays in compareExpressions.

## Packages

| Package | Import name | Responsibility | Depends on |
|---|---|---|---|
| `slr_parsing` | `slr_parsing` | Generic SLR(1) parser engine | — |
| `evaluation_result` | `evaluation_result` | Evaluation result container | — |
| `criteria` | `criteria` | Criteria DSL parser + evaluation graph | `slr_parsing` |
| `expression_parsing` | `expression_parsing` | SymPy parsing / preprocessing / LaTeX preview | `slr_parsing`, `sympy`, `latex2sympy2` |
| `units` | `units` | Unit-system data, physical-quantity parsing, dimensional analysis | `slr_parsing`, `expression_parsing`, `sympy` |

## Feedback decoupling

The parsing/units code was decoupled from compareExpressions' feedback strings.
Instead of resolving feedback text inline, functions surface an
`expression_parsing.FeedbackTag(tag, inputs)` namedtuple. Consumers own the
`tag -> string` mapping.

## Install (editable, in dependency order)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e slr_parsing -e evaluation_result -e criteria \
            -e expression_parsing -e units
```
