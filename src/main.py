from fastapi import FastAPI

from core.lifespan import lifespan
from core.middlewares import register_middlewares
from core.settings import settings

app = FastAPI(
    debug=settings.debug,
    title=settings.api_name,
    version=settings.api_version,
    lifespan=lifespan,
)

register_middlewares(app)


if __name__ == "__main__":
    if settings.debug:
        import uvicorn

        if settings.reverse_proxy:
            ssl_keyfile = None
            ssl_certfile = None
        else:
            ssl_keyfile = settings.private_key
            ssl_certfile = settings.public_key

        uvicorn.run(
            app="main:app",
            host=settings.host,
            port=settings.port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=True,
        )
