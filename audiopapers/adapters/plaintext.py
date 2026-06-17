"""Plain text / pasted text -> segments with a simple heading heuristic."""

from __future__ import annotations

import re

from audiopapers.cleaning import normalize_heading_text
from audiopapers.segments import Segment, body, heading, pack_body


def text_to_segments(text: str) -> list[Segment]:
    """Split text on blank lines; short non-terminating lines become level-2 headings, rest body."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    segs: list[Segment] = []
    for p in paras:
        if len(p) < 80 and not p.endswith("."):
            segs.append(heading(2, normalize_heading_text(p)))
        else:
            segs.append(body(p))
    return pack_body(segs)
