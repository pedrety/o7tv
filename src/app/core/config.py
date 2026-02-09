from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SRC_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
STATIC_DIR.mkdir(exist_ok=True)

TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_DIR))
STATIC_URL = "/static"
SEVENTV_GQL_URL = "https://api.7tv.app/v4/gql"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_prefix="APP_"
    )
