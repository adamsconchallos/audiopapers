"""EPUB -> segments. Ported from the build_epub.py prototype."""

from __future__ import annotations

import posixpath
import re
import zipfile

from audiopapers.cleaning import normalize_heading_text, strip_html
from audiopapers.segments import Segment, body, heading, pack_body

_BLOCK = re.compile(r"(?is)<h([1-6])\b[^>]*>(.*?)</h\1>|<p\b[^>]*>(.*?)</p>")
_SKIP = re.compile(r"(?is)<(script|style|head)[^>]*>.*?</\1>")


def _load_spine(z: zipfile.ZipFile) -> tuple[str, list[tuple[str, str]]]:
    """Return (opf_dir, [(idref, href), ...]) in reading order."""
    container = z.read("META-INF/container.xml").decode("utf-8", "replace")
    opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
    opf_dir = posixpath.dirname(opf_path)
    opf = z.read(opf_path).decode("utf-8", "replace")
    href_by_id = dict(re.findall(r'<item\b[^>]*\bid="([^"]+)"[^>]*\bhref="([^"]+)"', opf))
    for href, ident in re.findall(r'<item\b[^>]*\bhref="([^"]+)"[^>]*\bid="([^"]+)"', opf):
        href_by_id.setdefault(ident, href)
    spine = re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf)
    return opf_dir, [(idref, href_by_id.get(idref, "")) for idref in spine]


def _doc_segments(raw: str) -> list[Segment]:
    """Walk a document's HTML, yielding ordered heading/body segments."""
    raw = _SKIP.sub(" ", raw)
    segs: list[Segment] = []
    for m in _BLOCK.finditer(raw):
        if m.group(1):
            text = strip_html(m.group(2))
            if text:
                segs.append(heading(int(m.group(1)), normalize_heading_text(text)))
        else:
            text = strip_html(m.group(3))
            if text:
                segs.append(body(text))
    return segs


def epub_to_segments(path: str, include: list[str] | None = None) -> list[Segment]:
    """Extract segments from an EPUB in spine order; `include` filters by idref or filename stem."""
    with zipfile.ZipFile(path) as z:
        opf_dir, spine = _load_spine(z)
        inc = set(include) if include else None
        segs: list[Segment] = []
        for idref, href in spine:
            base = posixpath.splitext(posixpath.basename(href))[0]
            if inc is not None and idref not in inc and base not in inc:
                continue
            doc = posixpath.normpath(posixpath.join(opf_dir, href)) if opf_dir else href
            try:
                raw = z.read(doc).decode("utf-8", "replace")
            except KeyError:
                continue
            segs.extend(_doc_segments(raw))
        return pack_body(segs)
