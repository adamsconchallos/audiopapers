"""The common segment model and body-paragraph packing.

A Segment is an ordered unit of narration: {"kind", "level", "text"}.
  kind: "heading" or "body"
  level: 1-6 for headings, 0 for body
  text: the words to speak
Every input adapter emits a list[Segment]; pack_body() then merges adjacent
body paragraphs so each TTS request stays within MAX_CHARS.
"""

from __future__ import annotations

import re

Segment = dict
MAX_CHARS = 3500

_SENT = re.compile(r"(?<=[.!?])\s+")


def heading(level: int, text: str) -> Segment:
    return {"kind": "heading", "level": level, "text": text}


def body(text: str) -> Segment:
    return {"kind": "body", "level": 0, "text": text}


def pack_body(segments: list[Segment], max_chars: int = MAX_CHARS) -> list[Segment]:
    """Merge consecutive body paragraphs into <= max_chars chunks.

    Headings pass through in place. Over-long single paragraphs are split on
    sentence boundaries; a pathological sentence longer than max_chars is kept
    whole (the TTS chunker handles it downstream).
    """
    out: list[Segment] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf:
            out.append(body(buf))
            buf = ""

    for seg in segments:
        if seg["kind"] == "heading":
            flush()
            out.append(seg)
            continue
        para = seg["text"]
        if len(para) > max_chars:
            flush()
            piece = ""
            for sent in _SENT.split(para):
                if piece and len(piece) + len(sent) + 1 > max_chars:
                    out.append(body(piece))
                    piece = sent
                else:
                    piece = f"{piece} {sent}".strip()
            if piece:
                out.append(body(piece))
        elif not buf:
            buf = para
        elif len(buf) + len(para) + 2 <= max_chars:
            buf = f"{buf}\n\n{para}"
        else:
            flush()
            buf = para
    flush()
    return out
