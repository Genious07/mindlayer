from typing import List

from ..storage.base import BaseStorage, MemoryEntry


def resolve_conflicts(storage: BaseStorage, new_entry: MemoryEntry) -> None:
    candidates = storage.search(new_entry.content, limit=5)
    for existing in candidates:
        if existing.id == new_entry.id:
            continue
        if _is_duplicate(existing.content, new_entry.content):
            if existing.score >= new_entry.score:
                storage.delete(new_entry.id)
            else:
                storage.delete(existing.id)
            return


def _is_duplicate(a: str, b: str) -> bool:
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return False
    overlap = len(a_words & b_words) / min(len(a_words), len(b_words))
    return overlap > 0.8
