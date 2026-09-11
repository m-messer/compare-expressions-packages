# Changelog: compareexpressions-slr-parsing

## 0.2.0 (unreleased)

The first release after the extraction refactor. The import path is now `compareexpressions.slr_parsing` (was `slr_parsing`).

### Fixed

- `ExprNode` tag sets are no longer shared. Before, every node built without a tag handler shared the mutable default `tags=set()`, `copy()` shared the original's set, and `tag_transfer` returned a single child's own set as its parent's tags. Tagging one node could tag unrelated nodes.
- `str(ExprNode)` shows the node's tags whenever it has any; it used to hide them unless there were two or more. Empty tags print as `tags: {}` (was `tags:  {}`).
- A custom `expression_node` passed to the expression-parser builder no longer becomes a literal token. The implicit-multiplication convention parser in `expression_parsing` uses `"E"` as its node symbol, so every capital `E` in an input was scanned as a grammar symbol and inputs such as `2E` or `xE` failed to parse.
- `SLR_Parser` no longer sorts the caller's `token_list` in place.
- `scan()` raises `ValueError` for an unknown `mode` (it used to crash with `UnboundLocalError`), and matches the mode exactly rather than by substring.
- `group(0)` and `operate(0)` raise `ValueError`. `operate(0)` was accepted and would have consumed the entire output stack.
- Each production runs its own reduction action. Actions used to be looked up by production *body*, so two productions with the same body but different heads (such as `A -> x` and `B -> x`) both ran whichever action was defined last. None of the grammars in these packages had such a pair.
- `new_root_on_error` works: parsing resumes at the offending token and the extra roots are appended to the output. Before, the offending token was dropped and `parse()` crashed on the remaining tokens.

### Removed

- `package` reduction action: unused, and it stored the `repr` of its children list as the node content. Use `join` (merge into one node) or a custom action.
- `discard_output_until_on_error`: unused, and it could not work. It popped parser output without unwinding the state stack, so every use ended in `IndexError`.
