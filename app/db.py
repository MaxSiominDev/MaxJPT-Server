import aiosqlite
from datetime import datetime, timezone

DB_PATH = "/app/data/requests.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_prompt TEXT,
                model_response TEXT
            )
        """)
        await db.commit()


async def insert_request(user_prompt: str, model_response: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO requests (timestamp, user_prompt, model_response) VALUES (?, ?, ?)",
            (ts, user_prompt, model_response),
        )
        await db.commit()


async def fetch_all_requests() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, timestamp, user_prompt, model_response FROM requests ORDER BY id DESC"
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]
