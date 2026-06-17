"""URL -> segments. Fetch HTML, drop boilerplate, extract body."""

from __future__ import annotations

import re
import urllib.request

from audiopapers.adapters.epub import _doc_segments
from audiopapers.segments import Segment, pack_body

_BOILERPLATE = re.compile(r"(?is)<(nav|header|footer|aside)[^>]*>.*?</\1>")


def url_to_segments(url: str, *, opener=urllib.request.urlopen) -> list[Segment]:
    """Fetch HTML via opener, strip nav/header/footer/aside boilerplate, extract and pack body segments."""
    req = urllib.request.Request(url, headers={"User-Agent": "audiopapers/0.1"})
    with opener(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", "replace")
    raw = _BOILERPLATE.sub(" ", raw)
    return pack_body(_doc_segments(raw))
