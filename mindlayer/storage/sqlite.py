import json
import sqlite3
import struct
from datetime import datetime
from typing import List, Optional

from .base import BaseStorage, MemoryEntry


def _serialize(v: List[float]) -> bytes:
    return struct.pack(f"{len(v)}f", *v)


def _deserialize(b: bytes) -> List[float]:
    n = len(b) // 4
    return list(struct.unpack(f"{n}f", b))


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "mindlayer.db", embedding_dim: Optional[int] = None):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._vec_loaded = False
        self._init_schema()

    def _load_vec_extension(self) -> bool:
        if self._vec_loaded:
            return True
        try:
            import sqlite_vec
            self._conn.enable_load_extension(True)
            sqlite_vec.load(self._conn)
            self._conn.enable_load_extension(False)
            self._vec_loaded = True
            return True
        except Exception:
            return False

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
            CREATE TABLE IF NOT EXISTS vec_index (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL UNIQUE
            );
        """)
        self._conn.commit()

        if self.embedding_dim and self._load_vec_extension():
            self._conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories
                USING vec0(embedding float[{self.embedding_dim}])
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

        if entry.embedding and self.embedding_dim and self._vec_loaded:
            row = self._conn.execute(
                "SELECT rowid FROM vec_index WHERE memory_id = ?", (entry.id,)
            ).fetchone()
            if row:
                rowid = row["rowid"]
                self._conn.execute(
                    "DELETE FROM vec_memories WHERE rowid = ?", (rowid,)
                )
                self._conn.execute(
                    "INSERT INTO vec_memories(rowid, embedding) VALUES (?, ?)",
                    (rowid, _serialize(entry.embedding)),
                )
            else:
                self._conn.execute(
                    "INSERT INTO vec_index(memory_id) VALUES (?)", (entry.id,)
                )
                rowid = self._conn.execute(
                    "SELECT rowid FROM vec_index WHERE memory_id = ?", (entry.id,)
                ).fetchone()["rowid"]
                self._conn.execute(
                    "INSERT INTO vec_memories(rowid, embedding) VALUES (?, ?)",
                    (rowid, _serialize(entry.embedding)),
                )

        self._conn.commit()

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        row = self._conn.execute(
            "SELECT * FROM memories WHERE id = ?", (memory_id,)
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        layer: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        if query_embedding and self.embedding_dim and self._vec_loaded:
            return self._vector_search(query_embedding, layer, limit)
        return self._keyword_search(query, layer, limit)

    def _vector_search(
        self, query_embedding: List[float], layer: Optional[str], limit: int
    ) -> List[MemoryEntry]:
        try:
            knn_rows = self._conn.execute(
                "SELECT rowid, distance FROM vec_memories WHERE embedding MATCH ? AND k = ? ORDER BY distance",
                [_serialize(query_embedding), limit],
            ).fetchall()
        except sqlite3.OperationalError:
            return self._keyword_search("", layer, limit)

        if not knn_rows:
            return []

        rowids = [r["rowid"] for r in knn_rows]
        placeholders = ",".join("?" * len(rowids))
        layer_filter = "AND m.layer = ?" if layer else ""
        params: list = rowids[:]
        if layer:
            params.append(layer)

        rows = self._conn.execute(
            f"""
            SELECT m.* FROM memories m
            JOIN vec_index vi ON m.id = vi.memory_id
            WHERE vi.rowid IN ({placeholders})
            {layer_filter}
            """,
            params,
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def _keyword_search(self, query: str, layer: Optional[str], limit: int) -> List[MemoryEntry]:
        if not query.strip():
            if layer:
                return self.list_by_layer(layer, limit)
            rows = self._conn.execute(
                "SELECT * FROM memories ORDER BY score DESC LIMIT ?", (limit,)
            ).fetchall()
            return [self._row_to_entry(r) for r in rows]
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
        row = self._conn.execute(
            "SELECT rowid FROM vec_index WHERE memory_id = ?", (memory_id,)
        ).fetchone()
        if row and self._vec_loaded:
            self._conn.execute("DELETE FROM vec_memories WHERE rowid = ?", (row["rowid"],))
            self._conn.execute("DELETE FROM vec_index WHERE memory_id = ?", (memory_id,))
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
