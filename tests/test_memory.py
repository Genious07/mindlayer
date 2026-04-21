import pytest

import memcore
from memcore import MemCore
from memcore.extractors.rules import RulesExtractor
from memcore.storage.sqlite import SQLiteStorage


@pytest.fixture
def mem(tmp_path):
    m = MemCore(db_path=str(tmp_path / "test.db"))
    yield m
    m.close()


def test_add_and_search(mem):
    mem.add("My name is Alice and I prefer dark mode")
    results = mem.search("dark mode")
    assert len(results) > 0


def test_context_manager(tmp_path):
    with MemCore(db_path=str(tmp_path / "ctx.db")) as mem:
        ids = mem.add("I love Python")
        assert isinstance(ids, list)


def test_version():
    assert memcore.__version__ == "0.1.0"


def test_custom_extractor(tmp_path):
    class DummyExtractor:
        def extract(self, text):
            return ["dummy fact"]

    mem = MemCore(db_path=str(tmp_path / "dummy.db"), extractor=DummyExtractor())
    ids = mem.add("anything")
    assert len(ids) == 1
    mem.close()
