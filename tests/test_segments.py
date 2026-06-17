from audiopapers.segments import body, heading, pack_body, MAX_CHARS


def test_pack_merges_small_bodies():
    segs = [body("One."), body("Two."), body("Three.")]
    packed = pack_body(segs, max_chars=20)
    assert [s["text"] for s in packed] == ["One.\n\nTwo.\n\nThree."]


def test_pack_preserves_heading_order():
    segs = [heading(1, "Title."), body("A."), heading(2, "Sec."), body("B.")]
    packed = pack_body(segs)
    assert [(s["kind"], s["level"]) for s in packed] == [
        ("heading", 1), ("body", 0), ("heading", 2), ("body", 0),
    ]


def test_pack_splits_overlong_paragraph_on_sentences():
    para = "Sentence one is here. Sentence two is here. Sentence three is here."
    packed = pack_body([body(para)], max_chars=30)
    assert len(packed) >= 2
    assert all(len(s["text"]) <= 30 for s in packed)
    # No text lost.
    assert "".join(s["text"] for s in packed).replace(" ", "") \
        .startswith("Sentenceoneishere")


def test_max_chars_default():
    assert MAX_CHARS == 3500
