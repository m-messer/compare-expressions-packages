"""Turn the criteria reached during evaluation into feedback on a result object.

These helpers take over the criteria-specific parts of the retired
``evaluation_result`` package. They work with any object satisfying
:class:`ResultLike`, such as ``lf_toolkit.evaluation.Result``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .graph import CriteriaGraph


class ResultLike(Protocol):
    """The part of a result object the helpers need (``lf_toolkit.evaluation.Result`` fits)."""

    @property
    def tags(self) -> list[str] | None: ...

    def add_feedback(self, tag: str, feedback: str) -> None: ...


def resolve_feedback(
    graph: CriteriaGraph,
    tags: Mapping[str, Mapping[str, Any] | None],
    custom_feedback: Mapping[str, str] | None = None,
) -> list[tuple[str, str]]:
    """Feedback text for each reached criterion, as ``(tag, text)`` pairs.

    ``tags`` maps criterion labels to the inputs for their feedback string
    generators (as returned by ``CriteriaGraph.generate_feedback``).
    ``custom_feedback`` overrides the text for given tags. Text is stripped,
    and a generator returning ``None`` gives ``""``: the tag still counts as
    reached, it just has nothing to say.
    """
    custom_feedback = custom_feedback or {}
    resolved = []
    for tag, inputs in tags.items():
        if tag in custom_feedback:
            text: str | None = custom_feedback[tag]
        else:
            text = graph.criteria[tag].feedback_string_generator(inputs or {})
        resolved.append((tag, (text or "").strip()))
    return resolved


def add_feedback_from_tags(
    result: ResultLike,
    tags: Mapping[str, Mapping[str, Any] | None],
    graph: CriteriaGraph,
    custom_feedback: Mapping[str, str] | None = None,
) -> None:
    """Add the feedback for each reached criterion to ``result``.

    Tags already on the result are skipped, so feeding several graphs'
    feedback into one result keeps the first text for a shared tag. Blank
    feedback is added as ``""`` so that the tag is still recorded.
    """
    existing = set(result.tags or ())
    for tag, text in resolve_feedback(graph, tags, custom_feedback):
        if tag not in existing:
            result.add_feedback(tag, text)
            existing.add(tag)


def criteria_test_data(graphs: Mapping[str, CriteriaGraph]) -> dict[str, dict[str, str]]:
    """The criteria-graph payload for a result's test data (JSON and mermaid per graph).

    Merge it into the serialised result when test data is requested, e.g.
    ``{**result.to_dict(include_test_data=True), **criteria_test_data(graphs)}``.
    """
    return {
        "criteria_graphs": {name: graph.to_json() for name, graph in graphs.items()},
        "criteria_graphs_vis": {name: graph.to_mermaid() for name, graph in graphs.items()},
    }
