from app.services.chunking import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("a short document", max_length=2000, overlap=200) == ["a short document"]


def test_empty_text_yields_nothing():
    assert chunk_text("   ", max_length=2000, overlap=200) == []


def test_splits_on_paragraph_boundaries():
    text = "\n\n".join(["para " + str(i) + " " + "x" * 80 for i in range(10)])
    chunks = chunk_text(text, max_length=200, overlap=0)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
    assert "".join(chunks).count("para 0") == 1


def test_overlap_carries_tail_of_previous_chunk():
    text = "alpha " * 20 + "\n\n" + "bravo " * 12
    chunks = chunk_text(text, max_length=150, overlap=40)
    assert len(chunks) == 2
    assert "alpha" in chunks[1]
    assert "bravo" in chunks[1]


def test_overlap_is_dropped_when_it_would_overflow_the_window():
    text = "alpha " * 30 + "\n\n" + "bravo " * 30
    chunks = chunk_text(text, max_length=200, overlap=60)
    assert len(chunks) == 2
    assert "alpha" not in chunks[1]


def test_paragraph_longer_than_max_is_split():
    chunks = chunk_text("word " * 400, max_length=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_overlap_cannot_exceed_half_the_window():
    chunks = chunk_text("z" * 900, max_length=100, overlap=500)
    assert all(len(c) <= 100 for c in chunks)
    assert len(chunks) < 100


def test_every_chunk_starts_on_a_whole_word():
    words = "alpha bravo charlie delta echo foxtrot golf hotel india juliet".split()
    text = " ".join(words * 12)
    chunks = chunk_text(text, max_length=160, overlap=40)
    assert len(chunks) > 2
    assert all(chunk.split()[0] in words for chunk in chunks)
    assert all(chunk.split()[-1] in words for chunk in chunks)
    assert all(len(chunk) <= 160 for chunk in chunks)


def test_a_single_unbreakable_token_still_splits():
    chunks = chunk_text("q" * 900, max_length=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
