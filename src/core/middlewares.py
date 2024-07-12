from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings


def register_middlewares(app: FastAPI) -> None:
    # ================================|CORS middleware|================================= #
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
