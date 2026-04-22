from abc import ABC, abstractmethod
from typing import List


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Return a fixed-length embedding vector for the given text."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Dimensionality of the embedding vectors produced."""
        ...
