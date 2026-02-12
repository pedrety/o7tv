from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.emotes import router as emotes_router
from app.config.config import settings


def get_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI()

    settings.static_dir.mkdir(exist_ok=True)
    app.mount(
        settings.static_url,
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )

    # Mount assets directory
    assets_dir = Path(__file__).parent.parent.parent / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    app.include_router(emotes_router)

    return app


app = get_app()
