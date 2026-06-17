from audiopapers.tts import (
    DEFAULT_BASE_URL, SynthArgs, candidate_api_keys, chunk_text, synthesize,
)


def test_synth_args_defaults():
    a = SynthArgs()
    assert (a.model, a.voice, a.format, a.speed) == ("tts-1", "alloy", "mp3", 1.0)
    assert a.base_url == DEFAULT_BASE_URL


def test_candidate_keys_prefers_audiopapers_then_openai(monkeypatch):
    monkeypatch.setenv("AUDIOPAPERS_API_KEY", "k-ap")
    monkeypatch.setenv("OPENAI_API_KEY", "k-oa")
    assert candidate_api_keys() == ["k-ap", "k-oa"]


def test_candidate_keys_missing_raises(monkeypatch):
    monkeypatch.delenv("AUDIOPAPERS_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import pytest
    with pytest.raises(RuntimeError, match="AUDIOPAPERS_API_KEY"):
        candidate_api_keys()


def test_synthesize_posts_to_configured_base_url(monkeypatch):
    import audiopapers.tts as tts
    seen = {}

    class FakeResp:
        def read(self): return b"AUDIO"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=0):
        seen["url"] = req.full_url
        return FakeResp()

    monkeypatch.setattr(tts.urllib.request, "urlopen", fake_urlopen)
    synthesize("hi", SynthArgs(base_url="http://localhost:8880/v1"), ["Bearer good"])
    assert seen["url"] == "http://localhost:8880/v1/audio/speech"


def test_chunk_short_text_single_chunk():
    assert chunk_text("hello world", 3500) == ["hello world"]


def test_chunk_splits_long_text():
    text = "\n\n".join(f"Para {i} body text." for i in range(200))
    chunks = chunk_text(text, 200)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_synthesize_tries_keys_until_one_works(monkeypatch):
    import audiopapers.tts as tts
    calls = []

    class FakeResp:
        def __init__(self, data): self._d = data
        def read(self): return self._d
        def __enter__(self): return self
        def __exit__(self, *a): return False

    import urllib.error

    def fake_urlopen(req, timeout=0):
        key = req.headers["Authorization"]
        calls.append(key)
        if "good" not in key:
            raise urllib.error.HTTPError(req.full_url, 401, "bad", {}, None)
        return FakeResp(b"AUDIO")

    monkeypatch.setattr(tts.urllib.request, "urlopen", fake_urlopen)
    out = synthesize("hi", SynthArgs(), ["Bearer bad", "Bearer good"])
    assert out == b"AUDIO"
    assert len(calls) == 2
