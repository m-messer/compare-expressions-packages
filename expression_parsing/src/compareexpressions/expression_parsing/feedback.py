"""Feedback decoupling for the extracted packages.

The in-app modules resolved feedback strings inline by importing
``app.feedback.symbolic``. To keep the extracted packages app-agnostic, the
parsing code instead surfaces a lightweight ``FeedbackTag`` carrying the
feedback ``tag`` and the ``inputs`` needed to render it. The consumer
(e.g. compareExpressions) owns the tag -> string mapping via its own feedback
generators.
"""

from collections import namedtuple

# tag: str    - feedback identifier (matches app feedback generator keys)
# inputs: dict - values needed to render the feedback string
FeedbackTag = namedtuple("FeedbackTag", ["tag", "inputs"])

__all__ = ["FeedbackTag"]
