"""CLI: turn a Markdown/EPUB/URL/text source into a chaptered .m4b audiobook."""

from __future__ import annotations

import argparse
import os
import sys

from audiopapers.adapters import select_adapter
from audiopapers.config import load_config
from audiopapers.packaging import build_audiobook  # noqa: F401 — re-exported; tests monkeypatch this name
from audiopapers.segments import Segment


def derive_title(source: str, segments: list[Segment]) -> str:
    """Return the first level-1 heading text (period stripped), else the source filename stem."""
    for seg in segments:
        if seg["kind"] == "heading" and seg["level"] == 1:
            return seg["text"].rstrip(".")
    stem = os.path.splitext(os.path.basename(source))[0]
    return stem or "audiobook"


def build_out_path(source: str, out_dir: str) -> str:
    """Return <out_dir>/<source-stem>.m4b."""
    stem = os.path.splitext(os.path.basename(source))[0] or "audiobook"
    return os.path.join(out_dir, f"{stem}.m4b")


def main(argv: list[str] | None = None) -> int:
    """Parse args, select adapter, build the audiobook; return 0 on success, 1 if no segments."""
    ap = argparse.ArgumentParser(description="Build a chaptered .m4b audiobook.")
    ap.add_argument("source", help="Markdown/EPUB/text file or URL")
    ap.add_argument("--config", default=None, help="path to config JSON")
    ap.add_argument("--out", default=None, help="output folder (default: config out_dir)")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--bitrate", type=int, default=None, help="AAC kbps (48/32/24)")
    ap.add_argument("--chapter-level", type=int, default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--cover", default=None, help="cover image path")
    ap.add_argument("--include", default="", help="epub-only: comma-separated spine idrefs")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    out_dir = args.out or cfg.out_dir
    os.makedirs(out_dir, exist_ok=True)

    inc = [s.strip() for s in args.include.split(",") if s.strip()] or None
    loader = select_adapter(args.source, include=inc)
    segments = loader(args.source)
    if not segments:
        print("error: no segments parsed from source", file=sys.stderr)
        return 1

    title = args.title or derive_title(args.source, segments)
    out_path = build_out_path(args.source, out_dir)

    print(f"{len(segments)} segments -> {out_path}")
    result = build_audiobook(
        segments, out_path,
        title=title,
        author=args.author or cfg.author,
        voice=args.voice or cfg.voice,
        api_base_url=cfg.api_base_url,
        model=cfg.model,
        bitrate_k=args.bitrate or cfg.bitrate_k,
        chapter_level=args.chapter_level if args.chapter_level is not None else cfg.chapter_level,
        cover_path=args.cover,
    )
    print(f"wrote {result.out_path}: {result.chapter_count} chapters, "
          f"{result.duration_s/60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
