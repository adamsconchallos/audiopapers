"""Pipeline defaults, optionally overlaid from a JSON config file."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields

DEFAULT_CONFIG_NAME = "audiopapers.config.json"


@dataclass
class Config:
    out_dir: str = "."
    api_base_url: str = "https://api.openai.com/v1"
    model: str = "tts-1"
    voice: str = "alloy"
    bitrate_k: int = 48
    chapter_level: int = 2
    author: str = "AudioPapers"


def user_config_path() -> str:
    """Per-user config location.

    Windows: %APPDATA%\\audiopapers\\<name>. Otherwise $XDG_CONFIG_HOME/audiopapers/<name>,
    falling back to ~/.config/audiopapers/<name>.
    """
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "audiopapers", DEFAULT_CONFIG_NAME)


def load_config(path: str | None = None) -> Config:
    """Load defaults, overlaying the first config file found.

    With no explicit `path`, look in the current directory first, then the per-user
    location (`user_config_path`); the first file that exists wins. An explicit `path`
    is the only file consulted.
    """
    if path is not None:
        candidates = [path]
    else:
        candidates = [os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME), user_config_path()]
    cfg = Config()
    known = {f.name for f in fields(Config)}
    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate, encoding="utf-8") as fh:
                data = json.load(fh)
            for k, v in data.items():
                if k in known:
                    setattr(cfg, k, v)
            break
    return cfg


def write_starter_config(path: str) -> bool:
    """Write a starter config (the built-in defaults) to `path`.

    Return True if written, False if a file already exists there (left unchanged).
    """
    if os.path.exists(path):
        return False
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(asdict(Config()), fh, indent=2)
        fh.write("\n")
    return True
