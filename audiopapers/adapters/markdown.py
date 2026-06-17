"""Markdown -> segments. The primary input path for papers."""

from __future__ import annotations

import re

from audiopapers.cleaning import normalize_heading_text, strip_html
from audiopapers.segments import Segment, body, heading, pack_body

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE = re.compile(r"^```|^~~~")
_FOOTNOTE_DEF = re.compile(r"^\[\^[^\]]+\]:")
_HTML_COMMENT = re.compile(r"(?s)<!--.*?-->")


def _strip_inline(text: str) -> str:
    """Reduce inline markdown to spoken text."""
    text = _HTML_COMMENT.sub("", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)        # images -> dropped
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)     # links -> text
    text = re.sub(r"\[\^[^\]]+\]", "", text)                 # footnote refs
    text = re.sub(r"`([^`]*)`", r"\1", text)                 # inline code -> text
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)          # bold
    text = re.sub(r"(\*|_)(.+?)\1", r"\2", text)             # italic
    text = strip_html(text)                                  # any raw HTML + entities
    return text.strip()


def markdown_to_segments(text: str) -> list[Segment]:
    """Parse markdown into ordered heading/body segments."""
    lines = text.lstrip("﻿").replace("\r\n", "\n").split("\n")
    segs: list[Segment] = []
    para: list[str] = []
    in_fence = False

    def flush_para() -> None:
        if para:
            cleaned = _strip_inline(" ".join(para))
            if cleaned:
                segs.append(body(cleaned))
            para.clear()

    for line in lines:
        if _FENCE.match(line.strip()):
            in_fence = not in_fence
            flush_para()
            continue
        if in_fence:
            continue
        if _FOOTNOTE_DEF.match(line.strip()):
            continue
        m = _HEADING.match(line)
        if m:
            flush_para()
            level = len(m.group(1))
            htext = _strip_inline(m.group(2))
            if htext:
                segs.append(heading(level, normalize_heading_text(htext)))
            continue
        if not line.strip():
            flush_para()
            continue
        # Strip leading blockquote markers and list bullets.
        stripped = re.sub(r"^\s*([>\-\*\+]|\d+\.)\s+", "", line)
        para.append(stripped)
    flush_para()
    return pack_body(segs)
