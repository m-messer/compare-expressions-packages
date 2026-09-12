"""Criteria DSL parser and criteria (evaluation) graphs.

- :func:`build_criteria_parser` parses criteria such as
  ``response = answer where a = 2``.
- :class:`CriteriaGraph` links evaluations to the criteria they establish,
  runs them (:meth:`CriteriaGraph.generate_feedback`) and renders the graph.
- :mod:`~compareexpressions.criteria.feedback` turns reached criteria into
  feedback on a result object such as ``lf_toolkit.evaluation.Result``.

Extracted from compareExpressions (app/utility/criteria_parsing.py and
app/utility/criteria_graph_utilities.py).
"""

from .errors import CriteriaError, CriteriaEvaluationError, CriteriaGraphError
from .feedback import ResultLike, add_feedback_from_tags, criteria_test_data, resolve_feedback
from .grammar import build_criteria_parser
from .graph import CriteriaGraph
from .nodes import CriterionNode, Edge, EvaluationNode, Node, OutputNode
from .tree import CriteriaTree

__all__ = [
    "CriteriaError",
    "CriteriaEvaluationError",
    "CriteriaGraph",
    "CriteriaGraphError",
    "CriteriaTree",
    "CriterionNode",
    "Edge",
    "EvaluationNode",
    "Node",
    "OutputNode",
    "ResultLike",
    "add_feedback_from_tags",
    "build_criteria_parser",
    "criteria_test_data",
    "resolve_feedback",
]
