import zipfile
from pathlib import Path

from audiopapers.adapters.epub import epub_to_segments


def _make_epub(tmp_path) -> str:
    p = tmp_path / "book.epub"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0"?><container><rootfiles>'
                   '<rootfile full-path="OEBPS/content.opf"/></rootfiles></container>')
        z.writestr("OEBPS/content.opf",
                   '<package><manifest>'
                   '<item id="c1" href="ch1.xhtml"/>'
                   '<item id="c2" href="ch2.xhtml"/>'
                   '</manifest><spine>'
                   '<itemref idref="c1"/><itemref idref="c2"/>'
                   '</spine></package>')
        z.writestr("OEBPS/ch1.xhtml", "<html><body><h1>Chapter One</h1><p>First body[1].</p></body></html>")
        z.writestr("OEBPS/ch2.xhtml", "<html><body><h2>Chapter Two</h2><p>Second body.</p></body></html>")
    return str(p)


def test_epub_spine_order_and_segments(tmp_path):
    segs = epub_to_segments(_make_epub(tmp_path))
    kinds = [(s["kind"], s["level"]) for s in segs]
    assert kinds[0] == ("heading", 1)
    texts = [s["text"] for s in segs]
    assert any("First body" in t and "[1]" not in t for t in texts)
    assert any("Chapter Two" in t for t in texts)


def test_epub_include_filter(tmp_path):
    segs = epub_to_segments(_make_epub(tmp_path), include=["c2"])
    assert all("First body" not in s["text"] for s in segs)
    assert any("Second body" in s["text"] for s in segs)
