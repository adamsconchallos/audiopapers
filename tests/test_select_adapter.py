from pathlib import Path

from audiopapers.adapters import select_adapter


def test_md_routes_to_markdown(tmp_path):
    f = tmp_path / "p.md"
    f.write_text("# Title\n\nBody here.", encoding="utf-8")
    segs = select_adapter(str(f))(str(f))
    assert segs[0]["kind"] == "heading"


def test_url_routes_to_url():
    fn = select_adapter("https://example.com/article")
    assert fn.__name__ == "_url_loader"


def test_txt_routes_to_plaintext(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("Heading\n\nLong body paragraph that is clearly body text here.", encoding="utf-8")
    segs = select_adapter(str(f))(str(f))
    assert any(s["kind"] == "body" for s in segs)


def test_include_threads_to_epub(monkeypatch):
    captured = {}
    import audiopapers.adapters as adapters
    def fake_epub(path, include=None):
        captured["include"] = include
        return []
    monkeypatch.setattr(adapters, "epub_to_segments", fake_epub)
    select_adapter("book.epub", include=["c2"])("book.epub")
    assert captured["include"] == ["c2"]
