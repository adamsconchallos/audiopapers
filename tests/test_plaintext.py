from audiopapers.adapters.plaintext import text_to_segments


def test_short_line_becomes_heading():
    txt = "Introduction\n\nThis is a real paragraph of body text that goes on long enough."
    segs = text_to_segments(txt)
    assert segs[0]["kind"] == "heading"
    assert segs[0]["level"] == 2
    assert segs[1]["kind"] == "body"


def test_long_paragraphs_are_body():
    txt = "A" * 100 + "."
    segs = text_to_segments(txt)
    assert all(s["kind"] == "body" for s in segs)
