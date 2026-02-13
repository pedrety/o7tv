from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SRC_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        templates_dir (Path): Directory containing Jinja2 templates.
        static_dir (Path): Directory containing static assets.
        static_url (str): URL prefix for static files.
        seventv_gql_url (str): 7TV GraphQL API URL.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_prefix="APP__"
    )

    templates_dir: Path = PROJECT_ROOT / "templates"
    static_dir: Path = PROJECT_ROOT / "static"
    static_url: str = "/static"
    seventv_gql_url: str = "https://api.7tv.app/v4/gql"


settings = Settings()
