from ..storage.base import BaseStorage

PROMOTE_THRESHOLD = 3  # access count to promote working → episodic
EPISODIC_THRESHOLD = 10  # access count to promote episodic → semantic


def consolidate(storage: BaseStorage) -> None:
    for entry in storage.list_by_layer("working"):
        if entry.access_count >= PROMOTE_THRESHOLD:
            entry.layer = "episodic"
            storage.save(entry)

    for entry in storage.list_by_layer("episodic"):
        if entry.access_count >= EPISODIC_THRESHOLD:
            entry.layer = "semantic"
            storage.save(entry)
