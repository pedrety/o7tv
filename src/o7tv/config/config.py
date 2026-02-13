from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SRC_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_prefix="APP__"
    )

    templates_dir: Path = PROJECT_ROOT / "templates"
    seventv_gql_url: str = "https://api.7tv.app/v4/gql"


settings = Settings()
