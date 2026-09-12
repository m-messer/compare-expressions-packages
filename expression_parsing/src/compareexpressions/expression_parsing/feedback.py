"""Feedback surfaced by parsing, as tags for the consumer to render.

The packages don't carry compareExpressions' feedback text. Where the
original code produced a feedback string, it now returns a
:class:`FeedbackTag`: the tag plus the inputs needed to render it. The
consumer owns the tag -> text mapping.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FeedbackTagName(StrEnum):
    """Tags emitted by this package (members compare equal to their string values)."""

    BRACKET_NOTATION_MISMATCH = "BRACKET_NOTATION_MISMATCH"
    """Brackets closed with a different kind than opened (inputs: ``x``, the expression)."""

    ABSOLUTE_VALUE_NOTATION_AMBIGUITY = "ABSOLUTE_VALUE_NOTATION_AMBIGUITY"
    """``|...|`` pairs that could not be matched unambiguously (inputs: ``name``, e.g. ``"response"``)."""

    PARSE_ERROR = "PARSE_ERROR"
    """The expression could not be parsed (inputs: ``response``)."""


@dataclass(frozen=True)
class FeedbackTag:
    """A feedback tag and the inputs needed to render its text."""

    tag: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
