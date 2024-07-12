from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from core.settings import settings
from database.helper import db
from database.tables import create_table_user
from src.core.routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AbstractAsyncContextManager:
    db.init(settings.db.name)
    await db.connect()

    register_routers(app)

    await create_table_user(db.connection)

    yield

    await db.close()
