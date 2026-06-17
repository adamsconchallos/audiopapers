"""Shared text-cleaning helpers used by all input adapters."""

from __future__ import annotations

import html
import re

_TAG = re.compile(r"(?s)<[^>]+>")
_FOOTNOTE = re.compile(r"\[\d+\]")
_WS = re.compile(r"[ \t\xa0]+")


def strip_html(s: str) -> str:
    """Remove tags, unescape entities, drop footnote markers, collapse whitespace."""
    s = _TAG.sub(" ", s)
    s = html.unescape(s)
    s = _FOOTNOTE.sub("", s)
    s = s.replace("\r", "\n")
    s = re.sub(r"\s*\n\s*", " ", s)
    s = _WS.sub(" ", s)
    return s.strip()


def normalize_heading_text(s: str) -> str:
    """Make a heading read as a sentence: trim, drop trailing punctuation, add one period."""
    s = s.strip().rstrip("?!.")
    return f"{s}." if s else s
