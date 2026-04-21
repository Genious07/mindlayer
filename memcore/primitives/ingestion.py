import uuid
from datetime import datetime
from typing import List

from ..extractors.base import BaseExtractor
from ..storage.base import BaseStorage, MemoryEntry


def ingest(text: str, extractor: BaseExtractor, storage: BaseStorage, layer: str = "working") -> List[str]:
    facts = extractor.extract(text)
    ids = []
    now = datetime.utcnow()
    for fact in facts:
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=fact,
            layer=layer,
            score=1.0,
            created_at=now,
            last_accessed=now,
            access_count=0,
            metadata={},
        )
        storage.save(entry)
        ids.append(entry.id)
    return ids
