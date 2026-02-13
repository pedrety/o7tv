from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from o7tv.api.emotes import router as emotes_router


def get_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI()

    # Mount assets directory
    assets_dir = Path(__file__).parent.parent.parent / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    app.include_router(emotes_router)

    return app


app = get_app()
