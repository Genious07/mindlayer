from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class MemoryEntry:
    id: str
    content: str
    layer: str  # "working" | "episodic" | "semantic"
    score: float  # relevance/importance score
    created_at: datetime
    last_accessed: datetime
    access_count: int
    metadata: dict
    embedding: Optional[List[float]] = field(default=None, repr=False)


class BaseStorage(ABC):
    @abstractmethod
    def save(self, entry: MemoryEntry) -> None: ...

    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryEntry]: ...

    @abstractmethod
    def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        layer: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]: ...

    @abstractmethod
    def delete(self, memory_id: str) -> None: ...

    @abstractmethod
    def update_score(self, memory_id: str, score: float) -> None: ...

    @abstractmethod
    def list_by_layer(self, layer: str, limit: int = 100) -> List[MemoryEntry]: ...

    @abstractmethod
    def close(self) -> None: ...
