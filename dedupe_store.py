from __future__ import annotations

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_messages (
    source_chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_chat_id, message_id)
);
"""


class DedupeStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    async def has_processed(self, source_chat_id: int, message_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM processed_messages WHERE source_chat_id=? AND message_id=? LIMIT 1",
                (source_chat_id, message_id),
            ) as cur:
                row = await cur.fetchone()
        return row is not None

    async def mark_processed(self, source_chat_id: int, message_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO processed_messages (source_chat_id, message_id) VALUES (?, ?)",
                (source_chat_id, message_id),
            )
            await db.commit()
