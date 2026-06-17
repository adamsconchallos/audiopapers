"""Shared test fixtures. No test may hit the real TTS endpoint."""

from __future__ import annotations

import hashlib

import pytest


def _fake_audio_for(text: str) -> bytes:
    """Deterministic fake 'audio' bytes derived from the input text.

    Real audio is never produced in tests; callers that need real durations
    monkeypatch at the ffmpeg layer instead. This stub stands in for the raw
    bytes returned by tts.synthesize().
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Length proportional to text so caches/branches behave realistically.
    return digest * (1 + len(text) // 32)


@pytest.fixture
def fake_synthesize(monkeypatch):
    """Patch tts.synthesize to return deterministic fake bytes (no network)."""

    def _synth(text, args, api_keys):  # noqa: ANN001 - mirrors real signature
        return _fake_audio_for(text)

    import audiopapers.tts as tts_mod

    monkeypatch.setattr(tts_mod, "synthesize", _synth)
    return _synth
