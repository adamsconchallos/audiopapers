# tests/test_audio.py
from audiopapers.audio import (
    concat_m4a, duration_seconds, encode_aac, make_silence,
)


def test_make_silence_has_expected_duration(tmp_path):
    p = str(tmp_path / "sil.m4a")
    make_silence(1.0, p)
    d = duration_seconds(p)
    assert 0.85 <= d <= 1.15  # AAC priming/encoder slop tolerance


def test_concat_sums_durations(tmp_path):
    a, b, out = (str(tmp_path / n) for n in ("a.m4a", "b.m4a", "out.m4a"))
    make_silence(0.5, a)
    make_silence(0.7, b)
    concat_m4a([a, b], out)
    assert 1.0 <= duration_seconds(out) <= 1.4


def test_encode_aac_produces_playable_m4a(tmp_path):
    src = str(tmp_path / "src.m4a")
    make_silence(0.5, src)
    out = str(tmp_path / "enc.m4a")
    encode_aac(src, out, bitrate_k=32)
    assert duration_seconds(out) > 0.3
