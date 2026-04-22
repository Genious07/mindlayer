from abc import ABC, abstractmethod
from typing import List


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> List[str]:
        """Extract discrete memory facts from a block of text."""
        ...
