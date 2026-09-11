"""Criteria DSL parser and evaluation graph.

Extracted from compareExpressions:
- parsing.py  <- app/utility/criteria_parsing.py
- graph.py    <- app/utility/criteria_graph_utilities.py

Depends on the ``slr_parsing`` package for the underlying parser engine.
"""

from .parsing import generate_criteria_parser
from .graph import CriteriaGraph

__all__ = ["generate_criteria_parser", "CriteriaGraph"]
