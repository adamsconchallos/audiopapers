"""Compute .m4b chapter markers from a played timeline and write FFMETADATA."""

from __future__ import annotations

from typing import NamedTuple

from audiopapers.segments import Segment


class Chapter(NamedTuple):
    title: str
    start_ms: int
    end_ms: int


def compute_chapters(
    timeline: list[tuple[Segment, float, float]], chapter_level: int = 2
) -> list[Chapter]:
    """Open a chapter at each heading with level <= chapter_level.

    timeline: ordered (segment, start_s, end_s). Audio before the first
    qualifying heading becomes a leading 'Intro' chapter.
    """
    if not timeline:
        return []
    total_end = timeline[-1][2]
    marks: list[tuple[str, float]] = []  # (title, start_s)
    for seg, start_s, _ in timeline:
        if seg["kind"] == "heading" and seg["level"] <= chapter_level:
            marks.append((seg["text"], start_s))
    if not marks or marks[0][1] > 0:
        marks.insert(0, ("Intro", 0.0))
    chapters: list[Chapter] = []
    for i, (title, start_s) in enumerate(marks):
        end_s = marks[i + 1][1] if i + 1 < len(marks) else total_end
        chapters.append(Chapter(title, round(start_s * 1000), round(end_s * 1000)))
    return chapters


def _esc(value: str) -> str:
    """Escape FFMETADATA special chars: = ; # \\ and newline."""
    out = []
    for ch in value:
        if ch in "=;#\\\n":
            out.append("\\")
        out.append(ch)
    return "".join(out)


def write_ffmetadata(
    path: str, chapters: list[Chapter], *, title: str, author: str, genre: str = "Audiobook"
) -> None:
    """Write an FFMETADATA1 file with global tags and [CHAPTER] blocks."""
    lines = [";FFMETADATA1",
             f"title={_esc(title)}",
             f"artist={_esc(author)}",
             f"album={_esc(title)}",
             f"genre={_esc(genre)}"]
    for ch in chapters:
        lines += ["[CHAPTER]", "TIMEBASE=1/1000",
                  f"START={ch.start_ms}", f"END={ch.end_ms}",
                  f"title={_esc(ch.title)}"]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
