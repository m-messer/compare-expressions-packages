"""Grammar building blocks shared by parsers."""

from .tokens import Token


def catch_undefined(label, content, original, start, end):
    return Token(label, content, original, start, end)
