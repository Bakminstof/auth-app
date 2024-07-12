from pathlib import Path

from aiosqlite import Connection, connect


class DBHelper:
    def __init__(self) -> None:
        self.__db_path: Path | None = None
        self.__connection: Connection | None = None

    def init(self, db_path: Path):
        self.__db_path = db_path

    async def connect(self) -> None:
        if not self.__db_path:
            raise RuntimeError("Database not initialized")

        self.__connection = await connect(self.__db_path)

    async def close(self) -> None:
        if self.__connection:
            await self.__connection.close()
            self.__connection = None

    @property
    def connection(self) -> Connection:
        if self.__connection is None:
            raise RuntimeError("Database not connect")

        return self.__connection


db = DBHelper()
