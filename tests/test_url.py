from audiopapers.adapters.url import url_to_segments


class _Resp:
    def __init__(self, data): self._d = data
    def read(self): return self._d
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_url_extracts_body_skips_nav():
    html = (b"<html><body><nav><p>Menu link</p></nav>"
            b"<h1>Real Title</h1><p>Real body paragraph.</p>"
            b"<footer><p>Footer junk</p></footer></body></html>")
    segs = url_to_segments("http://x", opener=lambda req, timeout=0: _Resp(html))
    texts = [s["text"] for s in segs]
    assert any("Real Title" in t for t in texts)
    assert any("Real body paragraph" in t for t in texts)
    assert all("Menu link" not in t and "Footer junk" not in t for t in texts)
