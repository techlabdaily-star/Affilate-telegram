from __future__ import annotations

import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    affiliate_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS link_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_chat_id, message_id, url)
);

CREATE TABLE IF NOT EXISTS repost_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affiliate_url TEXT NOT NULL,
    message_text TEXT NOT NULL,
    next_post_at TIMESTAMP NOT NULL,
    sent INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class DedupeStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._initialized = False

    async def init(self) -> None:
        if self._initialized:
            return
        async with aiosqlite.connect(self._db_path) as db:
            # SCHEMA contains multiple CREATE TABLE statements; use executescript.
            await db.executescript(SCHEMA)
            await db.commit()
        self._initialized = True

    async def has_processed(self, source_chat_id: int, message_id: int) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT 1 FROM processed_deals WHERE source_chat_id=? AND message_id=? LIMIT 1",
                (source_chat_id, message_id),
            ) as cursor:
                row = await cursor.fetchone()
        return row is not None

    async def mark_processed(
        self,
        source_chat_id: int,
        message_id: int,
        affiliate_url: str | None = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO processed_deals (source_chat_id, message_id, affiliate_url)
                VALUES (?, ?, ?)
                """,
                (source_chat_id, message_id, affiliate_url),
            )
            await db.commit()

    async def record_link_seen(
        self,
        source_chat_id: int,
        message_id: int,
        url: str,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO link_observations (source_chat_id, message_id, url)
                VALUES (?, ?, ?)
                """,
                (source_chat_id, message_id, url),
            )
            await db.commit()

    async def get_link_stats(self, url: str) -> dict:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT
                    COUNT(*) as seen_count,
                    COUNT(DISTINCT source_chat_id) as source_count
                FROM link_observations
                WHERE url = ?
                """,
                (url,),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return {"seen_count": 0, "source_count": 0}
        return {"seen_count": row[0], "source_count": row[1]}

    async def schedule_repost(self, affiliate_url: str, message_text: str, hours_from_now: int) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO repost_queue (affiliate_url, message_text, next_post_at)
                VALUES (
                    ?,
                    ?,
                    DATETIME('now', printf('+%d hours', ?))
                )
                """,
                (affiliate_url, message_text, hours_from_now),
            )
            await db.commit()

    async def get_due_reposts(self) -> list[tuple[int, str, str]]:
        """
        Returns a list of (id, affiliate_url, message_text) for entries that are due and not sent.
        """
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT id, affiliate_url, message_text
                FROM repost_queue
                WHERE sent = 0 AND next_post_at <= DATETIME('now')
                """,
            ) as cursor:
                rows = await cursor.fetchall()
        return [(row[0], row[1], row[2]) for row in rows]

    async def mark_repost_sent(self, repost_id: int) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE repost_queue SET sent = 1 WHERE id = ?",
                (repost_id,),
            )
            await db.commit()

