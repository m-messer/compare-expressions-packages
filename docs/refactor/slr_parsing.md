# Phase 1: `compareexpressions.slr_parsing`

No dependencies. The source is currently a single `parser.py` (845 lines).

## Target modules

| Module | Contents |
|---|---|
| `tokens.py` | `Token`, `ExprNode`, traversal steps (`traverse_prefix/postfix/infix/group`) |
| `actions.py` | Reduction actions: `proceed, package, append, append_last, join, create_node, relabel, group, operate, infix, insert_infix, compose, flatten` |
| `tags.py` | Tag helpers, renamed `add_tag`, `remove_tag`, `replace_tag`, `inherit_tags`, `union_rule`, `intersection_rule` |
| `grammar.py` | NamedTuples `TokenRule(pattern, label, matcher=None)`, `Production(head, body, action)`, `ErrorHandler(condition, action)` |
| `parser.py` | `SLRParser`, with `__init__` split into `_check_duplicate_productions`, `_tokenise_productions`, `_classify_symbols`, `_compute_first`, `_compute_follow`, `_build_states`, `_build_table`, `_resolve_conflicts`, `_report_unreachable`. Also `scan`, `parse` and debug printers. |
| `builder.py` | `build_expression_parser(...)` |
| `errors.py` | `SLRError` → `GrammarError`, `ScanError`, `ParseError` (attributes `state`, `lookahead`, `stack`, `output`; the debug dump lives in `details()`), `new_root_on_error`, `discard_output_until_on_error` |

## Checklist

### Bugs (regression test first, one commit each)

- [ ] `ExprNode(tags=set())` is a mutable default shared by every node without a tag handler: `a.tags.add('X')` leaks onto unrelated nodes. `copy()` also shares the tags set.
- [ ] `SLR_expression_parser` does `undefined += (None,)` when it should extend `expression_node`, so the expression-node symbol becomes a literal token regex. The convention parser then scans `"E"` as `EXPRESSION_NODE`, and `parse_expression("2E")` crashes (end-to-end test in Phase 3).
- [ ] `parse()` with leftover tokens after ACCEPT does `output += ExprNode(self.parse(tokens), [])`, which always raises. Change it to `output += self.parse(tokens)`.
- [ ] `group(empty=True)` swaps the labels on its synthetic delimiter tokens.
- [ ] `SLRParser.__init__` sorts the caller's `token_list` in place. Copy it first.
- [ ] `scan()` with an unknown `mode` raises `UnboundLocalError`. Validate against `Literal["expression", "bnf"]`.
- [ ] `ExprNode.__str__` only shows tags when `len > 1`; it should be `len > 0`.
- [ ] `package()` does `"".join(str(children))`, which stringifies the whole list.
- [ ] `operate()` checks `< 0` but its message says "at least one". Make them agree.

### Restructure (no behaviour change)

- [ ] Split `parser.py` into the modules above.
- [ ] Break `SLRParser.__init__` into the named table-building steps.
- [ ] Precompute the catch-undefined token and the rule/symbol partition in `__init__`, not per `scan()`; compile regexes once; memoise `closure()` during table construction.
- [ ] Remove the dead `break` after `raise`, the duplicate `self.parsing_table =`, and the `state_string` / `state_string_list` duplication.
- [ ] Unreachable-state reporting uses `logging` instead of `print`.
- [ ] Bare `Exception` → `GrammarError` / `ScanError` / `ParseError`.
- [ ] Document that `Token.__eq__`/`__hash__` compare by label only; the parser relies on this.

### API (break freely, recorded in `CHANGELOG.md`)

- [ ] `SLR_Parser` → `SLRParser`
- [ ] `SLR_expression_parser` → `build_expression_parser`
- [ ] `costum_tokens` / `costum_productions` → `custom_tokens` / `custom_productions`
- [ ] Mutable default args (`nodes=[]`, `delimiters=["", ""]`, `error_handler=[]`) → `None`/tuples
- [ ] `default_error_action(parser, ...)` → a proper method
- [ ] Tag helper renames (see `tags.py` above)

### Types & lint

- [ ] Full type hints; `mypy --strict` clean.
- [ ] `ruff check` / `ruff format` clean.

### Tests to add

- [ ] FIRST/FOLLOW and table construction on a textbook grammar.
- [ ] Scanner: longest match, custom matcher, catch-undefined, undefined input without a catch-all → `ScanError`.
- [ ] Error-handler dispatch.
