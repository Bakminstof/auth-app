from fastapi import FastAPI

from apps.auth.router import router as auth_router
from apps.users.router import router as users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(
        auth_router,
        tags=["Auth"],
    )
    app.include_router(
        users_router,
        tags=["Users"],
    )
