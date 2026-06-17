"""ffmpeg/mutagen audio layer: encode to AAC, silence, durations, concat.

Uses the ffmpeg bundled by imageio-ffmpeg (no system install). There is no
bundled ffprobe, so durations are read with mutagen instead.
"""

from __future__ import annotations

import subprocess

import imageio_ffmpeg
from mutagen.mp4 import MP4

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SAMPLE_RATE = 24000


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args], check=True
    )


def encode_aac(raw_audio_path: str, out_path: str, bitrate_k: int = 48) -> None:
    """Transcode any input audio to AAC mono at SAMPLE_RATE, .m4a container."""
    run_ffmpeg([
        "-i", raw_audio_path,
        "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-c:a", "aac", "-b:a", f"{bitrate_k}k",
        "-movflags", "+faststart", out_path,
    ])


def make_silence(seconds: float, out_path: str, bitrate_k: int = 48) -> None:
    """Write an AAC silence clip of the given length."""
    run_ffmpeg([
        "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
        "-t", f"{seconds}", "-c:a", "aac", "-b:a", f"{bitrate_k}k",
        "-movflags", "+faststart", out_path,
    ])


def duration_seconds(path: str) -> float:
    """Length of an MP4/M4A in seconds, via mutagen."""
    return float(MP4(path).info.length)


def concat_m4a(paths: list[str], out_path: str, workdir: str | None = None) -> None:
    """Losslessly concatenate AAC .m4a parts into one MP4 audio stream."""
    import os
    import tempfile

    listdir = workdir or tempfile.gettempdir()
    listfile = os.path.join(listdir, "_concat.txt")
    with open(listfile, "w", encoding="utf-8") as fh:
        for p in paths:
            ap = os.path.abspath(p).replace("\\", "/")
            fh.write(f"file '{ap}'\n")
    run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", listfile,
        "-c", "copy", "-movflags", "+faststart", out_path,
    ])
