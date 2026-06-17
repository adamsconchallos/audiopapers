# tests/test_markdown.py
from pathlib import Path

from audiopapers.adapters.markdown import markdown_to_segments

SAMPLE = (Path(__file__).parent / "fixtures" / "sample.md").read_text(encoding="utf-8")


def test_headings_get_levels():
    segs = markdown_to_segments(SAMPLE)
    headings = [(s["level"], s["text"]) for s in segs if s["kind"] == "heading"]
    assert (1, "The Sample Paper.") in headings
    assert (2, "Methods.") in headings
    assert (3, "Sub-detail.") in headings
    assert (2, "Results.") in headings


def test_link_reduced_to_text_and_emphasis_stripped():
    segs = markdown_to_segments(SAMPLE)
    body = " ".join(s["text"] for s in segs if s["kind"] == "body")
    assert "introduction" in body
    assert "link" in body
    assert "https://example.com" not in body
    assert "*" not in body and "_" not in body
    assert "bold" in body and "**" not in body


def test_code_block_dropped():
    segs = markdown_to_segments(SAMPLE)
    text = " ".join(s["text"] for s in segs)
    assert "print(" not in text
    assert "inline code" in text  # inline code text kept, backticks gone
    assert "`" not in text


def test_footnote_and_bullets_cleaned():
    segs = markdown_to_segments(SAMPLE)
    text = " ".join(s["text"] for s in segs)
    assert "[^1]" not in text
    assert "This footnote definition is dropped" not in text
    assert "bullet one" in text and "- bullet" not in text


def test_leading_bom_does_not_break_first_heading():
    segs = markdown_to_segments("﻿# BOM Title\n\nBody paragraph here.")
    assert segs[0]["kind"] == "heading"
    assert segs[0]["level"] == 1
    assert segs[0]["text"] == "BOM Title."
