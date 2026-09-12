# Changelog: compareexpressions-criteria

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.criteria` (was `criteria`).

### Replaces `compareexpressions-evaluation-result`

The `evaluation_result` package is retired. Use `lf_toolkit.evaluation.Result` from [toolkit-python](https://github.com/lambda-feedback/toolkit-python) together with the new `compareexpressions.criteria.feedback` helpers. These type against a `ResultLike` protocol (`tags` + `add_feedback(tag, text)`), so this package doesn't depend on lf_toolkit.

| `EvaluationResult` (v0.1) | Replacement |
|---|---|
| `EvaluationResult()` | `lf_toolkit.evaluation.Result()` |
| `result.add_feedback((tag, text))` | `result.add_feedback(tag, text)` |
| `result.add_feedback_from_tags(tags, graph, custom_feedback)` | `criteria.feedback.add_feedback_from_tags(result, tags, graph, custom_feedback)` |
| `result.add_criteria_graph(name, graph)` + `serialise(include_test_data=True)` | `{**result.to_dict(include_test_data=True), **criteria.feedback.criteria_test_data({name: graph, ...})}` |
| `result.serialise()` / `result[key]` | `result.to_dict()` |
| `result.get_tags()` | `result.tags` |
| `result.get_feedback(tag)` (returned indices) | `result.get_feedback(tag)` (returns the texts) |
| `result.latex` / `result.simplified` | `Result(latex=..., simplified=...)`; join a list of simplified forms yourself (`", ".join(...)`) |

Behaviour differences to be aware of when adopting:

- **Blank feedback.** `EvaluationResult` recorded the tag of a criterion whose feedback was `None` or blank but left it out of the feedback string. `add_feedback_from_tags` keeps the tag by adding `""`, but lf_toolkit@ae52fa6's `Result.feedback` joins every entry with `<br>`, blanks included, so the string can contain empty segments until the [proposed upstream fix](../docs/refactor/upstream-lf-toolkit.md) lands.
- **Tags in `to_dict()`.** lf_toolkit only includes `tags` with `include_test_data=True`; `EvaluationResult.serialise()` always did.
- **Stripping.** Feedback text is stripped when resolved (it used to be stripped when serialised), so the stored texts are already trimmed.

### Fixed

- Rendering a `CriteriaGraph.Tree` to mermaid no longer empties the tree. The renderer used the root's own `outgoing` list as its work stack.
- `generate_criteria_parser` no longer extends the module-level default token list, so reserved words from one parser no longer leak into every later parser.
- `build_tree` on an unknown label raises a `ValueError` naming the label. It used to raise `AttributeError` from formatting the message with the missing node.
- `add_node` works for evaluation nodes (it read a nonexistent `sufficiencies` attribute) and keeps the node's `evaluate` function and a criterion's `feedback_string_generator` (both were dropped).
- Graph nodes are hashable and compare unequal to non-nodes, instead of raising `AttributeError`.
- A failing `evaluate` function raises `CriteriaEvaluationError` (with the original exception chained) instead of printing the evaluation label and the whole evaluations dict to stdout.
