from datetime import datetime
from typing import List, Optional

from ..storage.base import BaseStorage, MemoryEntry


def retrieve(
    query: str,
    storage: BaseStorage,
    layer: Optional[str] = None,
    limit: int = 10,
) -> List[MemoryEntry]:
    results = storage.search(query, layer=layer, limit=limit)
    now = datetime.utcnow()
    for entry in results:
        entry.access_count += 1
        entry.last_accessed = now
        storage.save(entry)
    return results
