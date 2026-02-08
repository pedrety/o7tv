from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.emotes import router as emotes_router
from app.core.config import STATIC_DIR, STATIC_URL


def get_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI()

    app.mount(STATIC_URL, StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(emotes_router)

    return app


app = get_app()
