from typing import List, Optional

from ..extractors.base import BaseExtractor
from ..extractors.rules import RulesExtractor
from ..primitives.consolidation import consolidate
from ..primitives.decay import decay
from ..primitives.ingestion import ingest
from ..primitives.retrieval import retrieve
from ..storage.base import BaseStorage, MemoryEntry
from ..storage.sqlite import SQLiteStorage


class MemCore:
    def __init__(
        self,
        db_path: str = "memcore.db",
        extractor: Optional[BaseExtractor] = None,
        storage: Optional[BaseStorage] = None,
        use_llm: bool = False,
    ):
        self.storage = storage or SQLiteStorage(db_path)

        if extractor:
            self.extractor = extractor
        elif use_llm:
            from ..extractors.llm import GemmaExtractor
            self.extractor = GemmaExtractor()
        else:
            self.extractor = RulesExtractor()

    def add(self, text: str) -> List[str]:
        """Ingest text and extract memories. Returns list of memory IDs."""
        return ingest(text, self.extractor, self.storage)

    def search(self, query: str, layer: Optional[str] = None, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query."""
        return retrieve(query, self.storage, layer=layer, limit=limit)

    def consolidate(self) -> None:
        """Promote memories across layers based on access patterns."""
        consolidate(self.storage)

    def decay(self) -> None:
        """Apply time-based score decay and prune stale memories."""
        decay(self.storage)

    def close(self) -> None:
        self.storage.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
