"""Tests for config module."""
import json
import os

from audiopapers.config import (
    Config,
    load_config,
    user_config_path,
    write_starter_config,
)


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


def test_user_config_path_windows(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setenv("APPDATA", r"C:\Users\x\AppData\Roaming")
    p = user_config_path().replace("\\", "/")
    assert p == "C:/Users/x/AppData/Roaming/audiopapers/audiopapers.config.json"


def test_user_config_path_xdg(monkeypatch):
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/home/x/.config")
    assert user_config_path().replace("\\", "/") == "/home/x/.config/audiopapers/audiopapers.config.json"


def test_load_config_falls_back_to_user_dir(tmp_path, monkeypatch):
    workdir = tmp_path / "work"
    workdir.mkdir()
    monkeypatch.chdir(workdir)  # cwd has no config file
    user_cfg = tmp_path / "user" / "audiopapers.config.json"
    user_cfg.parent.mkdir()
    user_cfg.write_text(json.dumps({"voice": "am_adam"}), encoding="utf-8")
    monkeypatch.setattr("audiopapers.config.user_config_path", lambda: str(user_cfg))
    assert load_config().voice == "am_adam"


def test_load_config_cwd_beats_user_dir(tmp_path, monkeypatch):
    workdir = tmp_path / "work"
    workdir.mkdir()
    (workdir / "audiopapers.config.json").write_text(
        json.dumps({"voice": "cwd_voice"}), encoding="utf-8")
    monkeypatch.chdir(workdir)
    user_cfg = tmp_path / "user" / "audiopapers.config.json"
    user_cfg.parent.mkdir()
    user_cfg.write_text(json.dumps({"voice": "user_voice"}), encoding="utf-8")
    monkeypatch.setattr("audiopapers.config.user_config_path", lambda: str(user_cfg))
    assert load_config().voice == "cwd_voice"


def test_write_starter_config_creates_and_is_idempotent(tmp_path):
    dest = tmp_path / "sub" / "audiopapers.config.json"
    assert write_starter_config(str(dest)) is True
    assert json.loads(dest.read_text(encoding="utf-8"))["model"] == "tts-1"
    # a second call must not overwrite an existing file
    dest.write_text('{"voice": "changed"}', encoding="utf-8")
    assert write_starter_config(str(dest)) is False
    assert json.loads(dest.read_text(encoding="utf-8"))["voice"] == "changed"
