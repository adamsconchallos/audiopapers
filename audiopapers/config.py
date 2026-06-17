"""Pipeline defaults, optionally overlaid from a JSON config file."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, fields

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


def load_config(path: str | None = None) -> Config:
    """Load defaults, overlaying any JSON file found at `path`."""
    if path is None:
        path = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)
    cfg = Config()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        known = {f.name for f in fields(Config)}
        for k, v in data.items():
            if k in known:
                setattr(cfg, k, v)
    return cfg
