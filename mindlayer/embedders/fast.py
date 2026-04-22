from typing import List

from .base import BaseEmbedder

MODEL_NAME = "BAAI/bge-small-en-v1.5"
DIMENSIONS = 384


class FastEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = MODEL_NAME):
        self._model_name = model_name
        self._model = None  # lazy load

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from fastembed import TextEmbedding
        except ImportError:
            raise ImportError("Install fastembed: pip install mindlayer[vector]")
        print(f"[mindlayer] Loading embedding model '{self._model_name}' (one-time download ~130MB)...")
        self._model = TextEmbedding(model_name=self._model_name)

    def embed(self, text: str) -> List[float]:
        self._load()
        return list(next(self._model.embed([text])))

    @property
    def dimensions(self) -> int:
        return DIMENSIONS
