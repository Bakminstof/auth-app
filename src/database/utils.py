from aiosqlite import Connection

from database.helper import db


async def get_connection() -> Connection:
    return db.connection
