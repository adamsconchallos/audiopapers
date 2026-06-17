"""End-to-end: a real markdown fixture through build_audiobook to a chaptered .m4b.

Uses a fake synth that returns REAL AAC bytes (via make_silence) so the full
stitch->mux path runs with real ffmpeg but no network. Satisfies the spec's
testing strategy: feed a known Markdown paper, assert chapter count + duration.
"""

from __future__ import annotations

from pathlib import Path

from mutagen.mp4 import MP4

from audiopapers.adapters.markdown import markdown_to_segments
from audiopapers.audio import make_silence
from audiopapers.packaging import build_audiobook

SAMPLE = (Path(__file__).parent / "fixtures" / "sample.md").read_text(encoding="utf-8")


def _real_aac_synth(tmp_path):
    """A synth(text, args, api_keys) returning real AAC bytes; length scales with text."""
    cache: dict[float, bytes] = {}

    def synth(text, args, api_keys):
        secs = max(0.4, min(3.0, len(text) / 50))
        key = round(secs, 1)
        if key not in cache:
            p = tmp_path / f"_src_{key}.m4a"
            make_silence(secs, str(p))
            cache[key] = p.read_bytes()
        return cache[key]

    return synth


def test_markdown_sample_builds_chaptered_m4b(tmp_path):
    segs = markdown_to_segments(SAMPLE)
    out = str(tmp_path / "sample.m4b")
    result = build_audiobook(
        segs, out, title="The Sample Paper", author="Tester",
        workdir=str(tmp_path / "work"), synth=_real_aac_synth(tmp_path),
    )
    m = MP4(out)
    # sample.md has #, ##, ## headings (### Sub-detail is pause-only) -> 3 chapters.
    assert result.chapter_count == 3
    assert [c.title for c in m.chapters] == ["The Sample Paper.", "Methods.", "Results."]
    assert result.duration_s > 1.0
