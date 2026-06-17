from audiopapers.chapters import Chapter, compute_chapters, write_ffmetadata
from audiopapers.segments import body, heading


def test_chapters_open_at_threshold_headings():
    timeline = [
        (heading(1, "Title."), 0.0, 1.0),
        (body("A."), 1.0, 5.0),
        (heading(2, "Methods."), 5.0, 6.0),
        (body("B."), 6.0, 9.0),
        (heading(3, "Sub."), 9.0, 9.5),   # deeper -> no chapter
        (body("C."), 9.5, 12.0),
    ]
    chs = compute_chapters(timeline, chapter_level=2)
    assert [c.title for c in chs] == ["Title.", "Methods."]
    assert chs[0].start_ms == 0
    assert chs[0].end_ms == 5000
    assert chs[1].start_ms == 5000
    assert chs[1].end_ms == 12000


def test_leading_audio_before_first_heading_gets_intro():
    timeline = [
        (body("Preamble."), 0.0, 3.0),
        (heading(1, "Title."), 3.0, 4.0),
        (body("A."), 4.0, 6.0),
    ]
    chs = compute_chapters(timeline, chapter_level=2)
    assert chs[0].title == "Intro"
    assert chs[0].start_ms == 0 and chs[0].end_ms == 3000
    assert chs[1].title == "Title."


def test_write_ffmetadata_contains_chapter_blocks(tmp_path):
    chs = [Chapter("Intro", 0, 3000), Chapter("Methods.", 3000, 9000)]
    p = str(tmp_path / "meta.txt")
    write_ffmetadata(p, chs, title="My Paper", author="Me")
    text = open(p, encoding="utf-8").read()
    assert ";FFMETADATA1" in text
    assert "title=My Paper" in text
    assert "artist=Me" in text
    assert text.count("[CHAPTER]") == 2
    assert "TIMEBASE=1/1000" in text
    assert "START=3000" in text and "END=9000" in text
    assert "title=Methods." in text
