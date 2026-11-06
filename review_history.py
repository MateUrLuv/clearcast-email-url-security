"""Local, content-free history for ClearCast reviews."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import sqlite3
import unicodedata
from pathlib import Path

from ml.url_model import normalized_url


class ReviewHistory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY,
                    reviewed_at TEXT NOT NULL,
                    item_type TEXT NOT NULL CHECK (item_type IN ('Email', 'URL')),
                    source TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    score REAL NOT NULL,
                    threshold REAL NOT NULL,
                    assessment TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS reviews_fingerprint "
                "ON reviews (item_type, fingerprint)"
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @staticmethod
    def fingerprint(item_type: str, content: str) -> str:
        normalized = unicodedata.normalize("NFKC", content)
        if item_type == "Email":
            normalized = " ".join(normalized.split()).casefold()
        else:
            normalized = normalized_url(normalized.strip())[0]
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def record(
        self,
        item_type: str,
        content: str,
        score: float,
        threshold: float,
        source: str,
    ) -> bool:
        """Store review metadata and return whether the exact item was seen."""
        if item_type not in {"Email", "URL"}:
            raise ValueError("Review type must be Email or URL.")
        fingerprint = self.fingerprint(item_type, content)
        assessment = (
            "Review as phishing" if score >= threshold
            else "Below the phishing decision threshold"
        )
        with self._connection() as connection:
            prior_count = connection.execute(
                "SELECT COUNT(*) FROM reviews WHERE item_type = ? AND fingerprint = ?",
                (item_type, fingerprint),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO reviews
                    (reviewed_at, item_type, source, fingerprint, score, threshold, assessment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    item_type,
                    source,
                    fingerprint,
                    float(score),
                    float(threshold),
                    assessment,
                ),
            )
        return prior_count > 0

    def recent(self, limit: int = 100):
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT reviewed_at, item_type, source, score, threshold, assessment,
                    (
                        SELECT COUNT(*)
                        FROM reviews AS earlier
                        WHERE earlier.item_type = current.item_type
                          AND earlier.fingerprint = current.fingerprint
                          AND earlier.id < current.id
                    ) AS prior_reviews
                FROM reviews AS current
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        columns = (
            "reviewed_at", "item_type", "source", "score", "threshold",
            "assessment", "prior_reviews",
        )
        return [dict(zip(columns, row)) for row in rows]

    def clear(self):
        with self._connection() as connection:
            connection.execute("DELETE FROM reviews")
