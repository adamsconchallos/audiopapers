from audiopapers.cleaning import strip_html, normalize_heading_text


def test_strip_html_removes_tags_entities_footnotes():
    raw = "<p>Hello&nbsp;<b>world</b>[12] &amp; more</p>"
    assert strip_html(raw) == "Hello world & more"


def test_strip_html_collapses_whitespace():
    assert strip_html("a\n\n  b\tc") == "a b c"


def test_normalize_heading_appends_single_period():
    assert normalize_heading_text("Introduction") == "Introduction."
    assert normalize_heading_text("Methods.") == "Methods."
    assert normalize_heading_text("Why now?!") == "Why now."
