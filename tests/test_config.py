"""Tests for config module."""
import json

from audiopapers.config import Config, load_config


def test_defaults_when_no_file(tmp_path):
    cfg = load_config(str(tmp_path / "missing.json"))
    assert cfg == Config()
    assert cfg.bitrate_k == 48 and cfg.chapter_level == 2


def test_overlay_from_file(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"voice": "ef_dora", "bitrate_k": 32}), encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg.voice == "ef_dora"
    assert cfg.bitrate_k == 32
    assert cfg.chapter_level == 2  # untouched default


def test_config_provider_defaults():
    from audiopapers.config import Config
    cfg = Config()
    assert cfg.api_base_url == "https://api.openai.com/v1"
    assert cfg.model == "tts-1"
    assert cfg.voice == "alloy"


def test_config_overrides_base_url(tmp_path):
    import json
    from audiopapers.config import load_config
    p = tmp_path / "audiopapers.config.json"
    p.write_text(json.dumps({
        "api_base_url": "http://localhost:8880/v1",
        "model": "kokoro",
        "voice": "af_heart",
    }), encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg.api_base_url == "http://localhost:8880/v1"
    assert cfg.model == "kokoro"
    assert cfg.voice == "af_heart"
