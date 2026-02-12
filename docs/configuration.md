# Configuration

Configuration is managed with `pydantic-settings` and loaded from environment
variables prefixed with `APP__`. A `.env` file is read automatically when
present.

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `APP__TEMPLATES_DIR` | Path to the Jinja2 templates directory. | `PROJECT_ROOT / templates` |
| `APP__STATIC_DIR` | Path to the static output directory. | `PROJECT_ROOT / static` |
| `APP__STATIC_URL` | URL prefix used to serve static files. | `/static` |
| `APP__SEVENTV_GQL_URL` | 7TV GraphQL API endpoint. | `https://api.7tv.app/v4/gql` |

## Defaults

If no environment variables are provided, the application uses the defaults
from `src/app/config/config.py`. The server ensures the static directory exists
at startup.
