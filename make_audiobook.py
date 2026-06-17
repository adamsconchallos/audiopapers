"""Back-compat entry point. Real implementation lives in audiopapers.cli."""

from __future__ import annotations

from audiopapers.cli import build_audiobook, build_out_path, derive_title, main

__all__ = ["build_audiobook", "build_out_path", "derive_title", "main"]

if __name__ == "__main__":
    raise SystemExit(main())
