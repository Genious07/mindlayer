import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional

from .base import BaseStorage, MemoryEntry


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "memcore.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                layer TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_layer ON memories(layer);
            CREATE INDEX IF NOT EXISTS idx_score ON memories(score DESC);
        """)
        self._conn.commit()

    def save(self, entry: MemoryEntry) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO memories
                (id, content, layer, score, created_at, last_accessed, access_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                entry.content,
                entry.layer,
                entry.score,
                entry.created_at.isoformat(),
                entry.last_accessed.isoformat(),
                entry.access_count,
                json.dumps(entry.metadata),
            ),
        )
        self._conn.commit()

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        row = self._conn.execute(
            "SELECT * FROM memories WHERE id = ?", (memory_id,)
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def search(self, query: str, layer: Optional[str] = None, limit: int = 10) -> List[MemoryEntry]:
        terms = query.lower().split()
        like_clauses = " AND ".join(["LOWER(content) LIKE ?" for _ in terms])
        params: list = [f"%{t}%" for t in terms]

        if layer:
            sql = f"SELECT * FROM memories WHERE {like_clauses} AND layer = ? ORDER BY score DESC LIMIT ?"
            params += [layer, limit]
        else:
            sql = f"SELECT * FROM memories WHERE {like_clauses} ORDER BY score DESC LIMIT ?"
            params += [limit]

        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def delete(self, memory_id: str) -> None:
        self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self._conn.commit()

    def update_score(self, memory_id: str, score: float) -> None:
        self._conn.execute(
            "UPDATE memories SET score = ?, last_accessed = ? WHERE id = ?",
            (score, datetime.utcnow().isoformat(), memory_id),
        )
        self._conn.commit()

    def list_by_layer(self, layer: str, limit: int = 100) -> List[MemoryEntry]:
        rows = self._conn.execute(
            "SELECT * FROM memories WHERE layer = ? ORDER BY score DESC LIMIT ?",
            (layer, limit),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"],
            content=row["content"],
            layer=row["layer"],
            score=row["score"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed=datetime.fromisoformat(row["last_accessed"]),
            access_count=row["access_count"],
            metadata=json.loads(row["metadata"]),
        )
