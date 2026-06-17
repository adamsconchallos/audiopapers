from pathlib import Path

import audiopapers.cli as cli
from audiopapers.segments import body, heading


def test_derive_title_prefers_h1():
    segs = [heading(1, "Real Title."), body("x")]
    assert cli.derive_title("whatever.md", segs) == "Real Title"


def test_derive_title_falls_back_to_filename():
    segs = [body("no headings here")]
    assert cli.derive_title("my_paper.md", segs) == "my_paper"


def test_build_out_path():
    out = cli.build_out_path("C:/docs/paper.md", "D:/Sync")
    assert out.replace("\\", "/") == "D:/Sync/paper.m4b"


def test_main_end_to_end(tmp_path, monkeypatch):
    # Stub build_audiobook so the CLI wiring is tested without ffmpeg/network.
    captured = {}

    def fake_build(segments, out_path, **kw):
        captured["out_path"] = out_path
        captured["kw"] = kw
        captured["nseg"] = len(segments)
        from audiopapers.packaging import BuildResult
        Path(out_path).write_bytes(b"x")
        return BuildResult(out_path, 2, 12.5)

    monkeypatch.setattr(cli, "build_audiobook", fake_build)

    src = tmp_path / "paper.md"
    src.write_text("# Title\n\nBody paragraph here.\n\n## Section\n\nMore body.", encoding="utf-8")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    rc = cli.main([str(src), "--out", str(out_dir), "--voice", "ef_dora"])
    assert rc == 0
    assert captured["kw"]["voice"] == "ef_dora"
    assert captured["kw"]["title"] == "Title"
    assert Path(captured["out_path"]).name == "paper.m4b"


def test_main_passes_provider_from_config(tmp_path, monkeypatch):
    import json
    captured = {}

    def fake_build(segments, out_path, **kw):
        captured["kw"] = kw
        from audiopapers.packaging import BuildResult
        Path(out_path).write_bytes(b"x")
        return BuildResult(out_path, 1, 1.0)

    monkeypatch.setattr(cli, "build_audiobook", fake_build)

    cfg = tmp_path / "audiopapers.config.json"
    cfg.write_text(json.dumps({"api_base_url": "http://localhost:8880/v1", "model": "kokoro"}), encoding="utf-8")
    src = tmp_path / "p.md"
    src.write_text("# T\n\nBody.", encoding="utf-8")
    out_dir = tmp_path / "o"; out_dir.mkdir()

    rc = cli.main([str(src), "--config", str(cfg), "--out", str(out_dir)])
    assert rc == 0
    assert captured["kw"]["api_base_url"] == "http://localhost:8880/v1"
    assert captured["kw"]["model"] == "kokoro"
