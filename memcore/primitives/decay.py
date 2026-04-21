from datetime import datetime, timedelta

from ..storage.base import BaseStorage

DECAY_RATE = 0.05          # score lost per day of non-access
MIN_SCORE = 0.1            # floor before pruning
PRUNE_THRESHOLD = 0.05     # entries below this score are deleted


def decay(storage: BaseStorage) -> None:
    now = datetime.utcnow()
    for layer in ("working", "episodic"):
        for entry in storage.list_by_layer(layer):
            days_idle = (now - entry.last_accessed).total_seconds() / 86400
            new_score = entry.score - (DECAY_RATE * days_idle)
            if new_score <= PRUNE_THRESHOLD:
                storage.delete(entry.id)
            else:
                storage.update_score(entry.id, max(new_score, MIN_SCORE))
