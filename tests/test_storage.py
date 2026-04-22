import sqlite3
import uuid
from datetime import datetime

import pytest

from mindlayer.storage.sqlite import SQLiteStorage
from mindlayer.storage.base import MemoryEntry


def _vec_available() -> bool:
    try:
        import sqlite_vec
        conn = sqlite3.connect(":memory:")
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        conn.close()
        return True
    except Exception:
        return False


requires_vec = pytest.mark.skipif(not _vec_available(), reason="sqlite-vec not loadable on this Python build")


@pytest.fixture
def storage(tmp_path):
    db = SQLiteStorage(str(tmp_path / "test.db"))
    yield db
    db.close()


@pytest.fixture
def vec_storage(tmp_path):
    db = SQLiteStorage(str(tmp_path / "vec_test.db"), embedding_dim=4)
    yield db
    db.close()


def _entry(content="test fact", layer="working", score=1.0, embedding=None):
    now = datetime.utcnow()
    return MemoryEntry(
        id=str(uuid.uuid4()),
        content=content,
        layer=layer,
        score=score,
        created_at=now,
        last_accessed=now,
        access_count=0,
        metadata={},
        embedding=embedding,
    )


def test_save_and_get(storage):
    e = _entry("I prefer dark mode")
    storage.save(e)
    result = storage.get(e.id)
    assert result is not None
    assert result.content == "I prefer dark mode"


def test_search(storage):
    storage.save(_entry("I prefer dark mode"))
    storage.save(_entry("I work in Berlin"))
    results = storage.search("dark mode")
    assert len(results) == 1
    assert "dark" in results[0].content


def test_delete(storage):
    e = _entry()
    storage.save(e)
    storage.delete(e.id)
    assert storage.get(e.id) is None


def test_list_by_layer(storage):
    storage.save(_entry("a", layer="working"))
    storage.save(_entry("b", layer="episodic"))
    working = storage.list_by_layer("working")
    assert len(working) == 1
    assert working[0].content == "a"


def test_update_score(storage):
    e = _entry(score=1.0)
    storage.save(e)
    storage.update_score(e.id, 0.5)
    updated = storage.get(e.id)
    assert updated.score == pytest.approx(0.5)


@requires_vec
def test_vector_search(vec_storage):
    vec_storage.save(_entry("dark mode preference", embedding=[1.0, 0.0, 0.0, 0.0]))
    vec_storage.save(_entry("lives in Berlin", embedding=[0.0, 1.0, 0.0, 0.0]))

    results = vec_storage.search("", query_embedding=[1.0, 0.0, 0.0, 0.0], limit=1)
    assert len(results) == 1
    assert "dark" in results[0].content


@requires_vec
def test_vector_delete_cleans_index(vec_storage):
    e = _entry("temp fact", embedding=[0.5, 0.5, 0.0, 0.0])
    vec_storage.save(e)
    vec_storage.delete(e.id)
    assert vec_storage.get(e.id) is None
