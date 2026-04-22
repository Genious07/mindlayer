import uuid
from datetime import datetime
from typing import List, Optional

from ..embedders.base import BaseEmbedder
from ..extractors.base import BaseExtractor
from ..storage.base import BaseStorage, MemoryEntry


def ingest(
    text: str,
    extractor: BaseExtractor,
    storage: BaseStorage,
    layer: str = "working",
    embedder: Optional[BaseEmbedder] = None,
) -> List[str]:
    facts = extractor.extract(text)
    ids = []
    now = datetime.utcnow()
    for fact in facts:
        embedding = embedder.embed(fact) if embedder else None
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=fact,
            layer=layer,
            score=1.0,
            created_at=now,
            last_accessed=now,
            access_count=0,
            metadata={},
            embedding=embedding,
        )
        storage.save(entry)
        ids.append(entry.id)
    return ids
