from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "experiments.db"


@dataclass(frozen=True)
class ExperimentRecord:
    commit_hash: str
    val_bpb: float
    memory_gb: float
    status: str
    description: str
    signature: str = ""
    hypothesis: str = ""
    lesson: str = ""


SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    commit_hash TEXT NOT NULL,
    val_bpb REAL NOT NULL,
    memory_gb REAL NOT NULL,
    status TEXT NOT NULL,
    description TEXT NOT NULL,
    signature TEXT NOT NULL DEFAULT '',
    hypothesis TEXT NOT NULL DEFAULT '',
    lesson TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    topic TEXT NOT NULL,
    note TEXT NOT NULL,
    experiment_id INTEGER,
    FOREIGN KEY(experiment_id) REFERENCES experiments(id)
);

CREATE TABLE IF NOT EXISTS paper_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL,
    query TEXT NOT NULL DEFAULT ''
);
"""


class ExperimentDB:
    def __init__(self, path: Path = DEFAULT_DB_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(experiments)")}
        if "signature" not in columns:
            self.conn.execute(
                "ALTER TABLE experiments ADD COLUMN signature TEXT NOT NULL DEFAULT ''"
            )

    def close(self) -> None:
        self.conn.close()

    def add_experiment(self, record: ExperimentRecord) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO experiments (
                commit_hash, val_bpb, memory_gb, status, description, signature, hypothesis, lesson
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.commit_hash,
                record.val_bpb,
                record.memory_gb,
                record.status,
                record.description,
                record.signature,
                record.hypothesis,
                record.lesson,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_observation(self, *, topic: str, note: str, experiment_id: int | None = None) -> None:
        self.conn.execute(
            "INSERT INTO observations (topic, note, experiment_id) VALUES (?, ?, ?)",
            (topic, note, experiment_id),
        )
        self.conn.commit()

    def add_paper_note(
        self,
        *,
        title: str,
        summary: str,
        url: str = "",
        tags: str = "",
        query: str = "",
    ) -> None:
        self.conn.execute(
            "INSERT INTO paper_notes (title, url, tags, summary, query) VALUES (?, ?, ?, ?, ?)",
            (title, url, tags, summary, query),
        )
        self.conn.commit()

    def paper_notes_by_tag(self, tag: str, limit: int = 10) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            """
            SELECT * FROM paper_notes
            WHERE tags LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (f"%{tag}%", limit),
        )
        return list(cursor.fetchall())

    def recent_experiments(self, limit: int = 10) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            """
            SELECT * FROM experiments
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return list(cursor.fetchall())

    def best_experiment(self) -> sqlite3.Row | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM experiments
            WHERE status = 'keep'
            ORDER BY val_bpb ASC
            LIMIT 1
            """
        )
        return cursor.fetchone()

    def has_description(self, description: str) -> bool:
        cursor = self.conn.execute(
            "SELECT 1 FROM experiments WHERE description = ? LIMIT 1",
            (description,),
        )
        return cursor.fetchone() is not None

    def has_signature(self, signature: str) -> bool:
        cursor = self.conn.execute(
            "SELECT 1 FROM experiments WHERE signature = ? LIMIT 1",
            (signature,),
        )
        return cursor.fetchone() is not None

    def observations_by_topic(self, topic: str, limit: int = 10) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            """
            SELECT * FROM observations
            WHERE topic = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (topic, limit),
        )
        return list(cursor.fetchall())
