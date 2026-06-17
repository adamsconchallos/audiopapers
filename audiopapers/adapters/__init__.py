"""Input adapters: each turns a source into a list[Segment].

select_adapter(path) picks by file extension; URL strings route to the url
adapter. The registry is extended as adapters are added in later tasks.
"""

from __future__ import annotations

from collections.abc import Callable

from audiopapers.adapters.epub import epub_to_segments
from audiopapers.adapters.markdown import markdown_to_segments
from audiopapers.adapters.plaintext import text_to_segments
from audiopapers.adapters.url import url_to_segments
from audiopapers.segments import Segment


def _read(path: str) -> str:
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def select_adapter(source: str, *, include: list[str] | None = None) -> Callable[[str], list[Segment]]:
    """Pick an adapter by source: URL scheme or file extension. `include` filters EPUB spine items."""
    low = source.lower()
    if low.startswith(("http://", "https://")):
        def _url_loader(src: str) -> list[Segment]:
            return url_to_segments(src)
        return _url_loader
    if low.endswith((".md", ".markdown")):
        def _md_loader(src: str) -> list[Segment]:
            return markdown_to_segments(_read(src))
        return _md_loader
    if low.endswith(".epub"):
        def _epub_loader(src: str) -> list[Segment]:
            return epub_to_segments(src, include=include)
        return _epub_loader
    def _text_loader(src: str) -> list[Segment]:
        return text_to_segments(_read(src))
    return _text_loader
