import re

from app.core.config import settings

_PARAGRAPH = re.compile(r"\n\s*\n")


def chunk_text(text: str, max_length: int | None = None, overlap: int | None = None) -> list[str]:
    max_length = max_length or settings.CHUNK_MAX_LENGTH
    overlap = overlap if overlap is not None else settings.CHUNK_OVERLAP
    overlap = min(overlap, max_length // 2)

    text = text.strip()
    if not text:
        return []
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current = ""
    for paragraph in (p.strip() for p in _PARAGRAPH.split(text)):
        if not paragraph:
            continue
        if len(paragraph) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_words(paragraph, max_length, overlap))
            continue
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_length:
            current = candidate
            continue
        chunks.append(current)
        current = _join(_tail(current, overlap), paragraph, "\n\n", max_length)
    if current:
        chunks.append(current)
    return chunks


def _split_words(text: str, max_length: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for word in text.split():
        if len(word) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_characters(word, max_length, overlap))
            continue
        candidate = f"{current} {word}" if current else word
        if len(candidate) <= max_length:
            current = candidate
            continue
        chunks.append(current)
        current = _join(_tail(current, overlap), word, " ", max_length)
    if current:
        chunks.append(current)
    return chunks


def _split_characters(text: str, max_length: int, overlap: int) -> list[str]:
    step = max(max_length - overlap, 1)
    return [text[start : start + max_length] for start in range(0, len(text), step) if text[start : start + max_length]]


def _tail(chunk: str, overlap: int) -> str:
    if not overlap:
        return ""
    tail = chunk[-overlap:]
    _, separator, after = tail.partition(" ")
    return (after if separator else tail).strip()


def _join(tail: str, addition: str, separator: str, max_length: int) -> str:
    if not tail:
        return addition
    combined = f"{tail}{separator}{addition}"
    return combined if len(combined) <= max_length else addition
