"""Orchestrate segments -> cached AAC -> stitched .m4b with chapters/metadata."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

from mutagen.mp4 import MP4, MP4Cover

from audiopapers import tts
from audiopapers.audio import (
    concat_m4a, duration_seconds, encode_aac, make_silence, run_ffmpeg,
)
from audiopapers.chapters import compute_chapters, write_ffmetadata
from audiopapers.segments import Segment

GAP_BEFORE_HEADING = {1: 1.0, 2: 0.7, 3: 0.5, 4: 0.5, 5: 0.5, 6: 0.5}
GAP_AFTER_HEADING = 0.6
GAP_BODY = 0.35


@dataclass
class BuildResult:
    out_path: str
    chapter_count: int
    duration_s: float


def _gap_between(prev: Segment | None, cur: Segment) -> float:
    """Silence (seconds) to insert before `cur`."""
    if prev is None:
        return 0.0
    if cur["kind"] == "heading":
        return GAP_BEFORE_HEADING.get(cur["level"], 0.5)
    if prev["kind"] == "heading":
        return GAP_AFTER_HEADING
    return GAP_BODY


def build_audiobook(
    segments: list[Segment],
    out_path: str,
    *,
    title: str,
    author: str,
    voice: str = "af_heart",
    api_base_url: str = "https://api.openai.com/v1",
    model: str = "tts-1",
    bitrate_k: int = 48,
    chapter_level: int = 2,
    workdir: str | None = None,
    cover_path: str | None = None,
    synth=None,
) -> BuildResult:
    """Synthesize, cache, stitch, and package segments into a chaptered .m4b."""
    using_default_synth = synth is None
    synth = synth or tts.synthesize
    work = workdir or tempfile.mkdtemp(prefix="audiopapers_")
    os.makedirs(work, exist_ok=True)
    args = tts.SynthArgs(voice=voice, model=model, format="mp3", timeout=180, base_url=api_base_url)
    api_keys = tts.candidate_api_keys() if using_default_synth else []

    # Pre-render silence clips (one per distinct gap length).
    sil_cache: dict[float, str] = {}

    def silence(seconds: float) -> str:
        key = round(seconds, 3)
        if key not in sil_cache:
            p = os.path.join(work, f"sil_{key}.m4a")
            if not os.path.exists(p):
                make_silence(seconds, p, bitrate_k=bitrate_k)
            sil_cache[key] = p
        return sil_cache[key]

    parts: list[str] = []                         # ordered .m4a paths to concat
    timeline: list[tuple[Segment, float, float]] = []
    cursor = 0.0
    prev: Segment | None = None

    for i, seg in enumerate(segments):
        gap = _gap_between(prev, seg)
        if gap > 0:
            sp = silence(gap)
            parts.append(sp)
            cursor += duration_seconds(sp)

        seg_path = os.path.join(work, f"seg_{i:04d}.m4a")
        if not (os.path.exists(seg_path) and os.path.getsize(seg_path) > 0):
            raw = synth(seg["text"], args, api_keys)
            raw_path = os.path.join(work, f"seg_{i:04d}.src")
            with open(raw_path, "wb") as fh:
                fh.write(raw)
            encode_aac(raw_path, seg_path, bitrate_k=bitrate_k)
            os.remove(raw_path)

        start = cursor
        dur = duration_seconds(seg_path)
        cursor += dur
        parts.append(seg_path)
        timeline.append((seg, start, cursor))
        prev = seg

    # Concatenate everything losslessly.
    merged = os.path.join(work, "_merged.m4a")
    concat_m4a(parts, merged, workdir=work)

    # Compute chapters and mux them + metadata into the final .m4b.
    chapters = compute_chapters(timeline, chapter_level=chapter_level)
    meta_path = os.path.join(work, "_chapters.ffmeta")
    write_ffmetadata(meta_path, chapters, title=title, author=author)
    run_ffmpeg([
        "-i", merged, "-i", meta_path,
        "-map", "0", "-map_metadata", "1",
        "-c", "copy", out_path,
    ])

    if cover_path:
        write_cover(out_path, cover_path)

    return BuildResult(out_path, len(chapters), duration_seconds(out_path))


def write_cover(m4b_path: str, cover_path: str) -> None:
    """Embed a JPEG/PNG cover image into the .m4b via mutagen."""
    fmt = MP4Cover.FORMAT_PNG if cover_path.lower().endswith(".png") else MP4Cover.FORMAT_JPEG
    with open(cover_path, "rb") as fh:
        data = fh.read()
    mp4 = MP4(m4b_path)
    mp4["covr"] = [MP4Cover(data, imageformat=fmt)]
    mp4.save()
