# tests/test_packaging.py
from pathlib import Path

from mutagen.mp4 import MP4

from audiopapers.audio import make_silence
from audiopapers.packaging import build_audiobook
from audiopapers.segments import body, heading


def _fake_synth_factory(tmp_path):
    """Return a synth(text, args, api_keys) producing real AAC bytes.

    Length scales with text so durations vary; reuses ffmpeg via make_silence.
    """
    cache = {}

    def synth(text, args, api_keys):
        secs = max(0.4, min(3.0, len(text) / 50))
        key = round(secs, 1)
        if key not in cache:
            p = tmp_path / f"_src_{key}.m4a"
            make_silence(secs, str(p))
            cache[key] = p.read_bytes()
        return cache[key]

    return synth


def test_build_audiobook_makes_m4b_with_chapters(tmp_path):
    segs = [
        heading(1, "The Title."),
        body("Intro paragraph body text that is reasonably long."),
        heading(2, "Methods."),
        body("Methods body paragraph here."),
        heading(2, "Results."),
        body("Results body paragraph here."),
    ]
    out = str(tmp_path / "book.m4b")
    result = build_audiobook(
        segs, out, title="The Title", author="Tester",
        workdir=str(tmp_path / "work"),
        synth=_fake_synth_factory(tmp_path),
    )
    assert Path(out).exists()
    # 3 qualifying headings (#, ##, ##) -> 3 chapters.
    assert result.chapter_count == 3
    mp4 = MP4(out)
    assert mp4.chapters is not None
    assert len(mp4.chapters) == 3
    assert mp4.chapters[1].title == "Methods."
    assert mp4.tags["\xa9nam"][0] == "The Title"
    assert result.duration_s > 1.0


def test_build_resumes_from_cache(tmp_path):
    calls = {"n": 0}
    base = _fake_synth_factory(tmp_path)

    def counting_synth(text, args, api_keys):
        calls["n"] += 1
        return base(text, args, api_keys)

    segs = [heading(1, "T."), body("Body one."), body("Body two.")]
    work = str(tmp_path / "w")
    out = str(tmp_path / "b.m4b")
    build_audiobook(segs, out, title="T", author="A", workdir=work, synth=counting_synth)
    first = calls["n"]
    # Second build reuses cached seg_*.m4a -> no new synth calls.
    build_audiobook(segs, out, title="T", author="A", workdir=work, synth=counting_synth)
    assert calls["n"] == first
