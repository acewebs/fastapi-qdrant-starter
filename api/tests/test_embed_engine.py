import pytest

from app.core.config import settings


@pytest.mark.parametrize(
    "engine,key,expected,dim",
    [
        ("auto", None, "fastembed", 384),
        ("auto", "sk-test", "openai", 1024),
        ("fastembed", "sk-test", "fastembed", 384),
        ("openai", None, "openai", 1024),
    ],
)
def test_engine_resolution(monkeypatch, engine, key, expected, dim):
    monkeypatch.setattr(settings, "EMBED_ENGINE", engine)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", key)
    assert settings.embed_engine == expected
    assert settings.embedding_dimensions == dim
