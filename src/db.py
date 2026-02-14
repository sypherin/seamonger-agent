import sqlite3
from contextlib import contextmanager
from pathlib import Path

from src.models import Fisherman


class FishermanMemory:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_parent_dir()
        self.init_schema()

    def _ensure_parent_dir(self) -> None:
        path = Path(self.db_path)
        if path.parent and str(path.parent) != ".":
            path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fisherman_memory (
                    fisherman_id TEXT PRIMARY KEY,
                    specialty TEXT NOT NULL,
                    reliability_score REAL NOT NULL DEFAULT 0.5
                )
                """
            )
            conn.commit()

    def upsert_fisherman(self, fisherman: Fisherman) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO fisherman_memory (fisherman_id, specialty, reliability_score)
                VALUES (?, ?, ?)
                ON CONFLICT(fisherman_id) DO UPDATE SET
                    specialty = excluded.specialty,
                    reliability_score = excluded.reliability_score
                """,
                (fisherman.fisherman_id, fisherman.specialty, fisherman.reliability_score),
            )
            conn.commit()

    def get_fisherman(self, fisherman_id: str) -> Fisherman | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT fisherman_id, specialty, reliability_score FROM fisherman_memory WHERE fisherman_id = ?",
                (fisherman_id,),
            ).fetchone()
        if row is None:
            return None
        return Fisherman(
            fisherman_id=row["fisherman_id"],
            specialty=row["specialty"],
            reliability_score=float(row["reliability_score"]),
        )

    def list_fishermen(self) -> list[Fisherman]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT fisherman_id, specialty, reliability_score FROM fisherman_memory ORDER BY reliability_score DESC"
            ).fetchall()
        return [
            Fisherman(
                fisherman_id=row["fisherman_id"],
                specialty=row["specialty"],
                reliability_score=float(row["reliability_score"]),
            )
            for row in rows
        ]
