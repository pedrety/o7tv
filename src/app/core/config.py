from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = SRC_DIR / "templates"
STATIC_DIR = SRC_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_DIR))
STATIC_URL = "/static"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_prefix="APP_"
    )
