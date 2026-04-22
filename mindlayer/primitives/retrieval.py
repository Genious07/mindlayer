from datetime import datetime
from typing import List, Optional

from ..embedders.base import BaseEmbedder
from ..storage.base import BaseStorage, MemoryEntry


def retrieve(
    query: str,
    storage: BaseStorage,
    layer: Optional[str] = None,
    limit: int = 10,
    embedder: Optional[BaseEmbedder] = None,
) -> List[MemoryEntry]:
    query_embedding = embedder.embed(query) if embedder else None
    results = storage.search(query, query_embedding=query_embedding, layer=layer, limit=limit)
    now = datetime.utcnow()
    for entry in results:
        entry.access_count += 1
        entry.last_accessed = now
        storage.save(entry)
    return results
