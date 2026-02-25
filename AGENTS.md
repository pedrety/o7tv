# PROJECT KNOWLEDGE BASE

## OVERVIEW
FastAPI (Python 3.12) service that converts 7TV emotes to streamed WebM responses.
Uses `uv` for dependency management, `ffmpeg` for conversion, and Jinja2 + Tailwind CDN
for the minimal UI.

## STRUCTURE
```
o7tv/
├── src/o7tv/              # FastAPI app package
├── templates/             # Jinja templates (base/home/results/convert)
├── assets/                # Icon + static assets served via /assets
├── docs/                  # API/conversion/config/error docs
├── static/                # Optional output mount (streaming by default)
├── Dockerfile             # Container build/run
├── pyproject.toml          # Tooling + deps
└── uv.lock                # Dependency lock
```

## WHERE TO LOOK
| Task | Location | Notes |
| --- | --- | --- |
| App factory | `src/o7tv/main.py` | `get_app()` + module `app` |
| Routes | `src/o7tv/api/emotes.py` | All endpoints mounted at `/` |
| 7TV search | `src/o7tv/services/seventv.py` | GraphQL search + image selection |
| Conversion | `src/o7tv/services/conversion.py` | `ffmpeg` streaming pipeline |
| URL validation | `src/o7tv/utils/http.py` | Allowed hosts + safe filenames |
| Templates | `templates/*.html` | Base template defines blocks + JS helpers |
| Docs | `docs/*.md` | API, conversion, configuration, errors |

## CONVENTIONS (DEVIATIONS)
- Use `uv` (`uv sync`, `uv add/remove`); `uv.lock` is the source of truth.
- Ruff line length is 100 and quote style is double; pre-commit runs ruff + mypy.
- Settings are loaded via `pydantic-settings` with `APP__` env prefix.
- Templates extend `base.html` and use `sidebar/content/scripts` blocks.
- Allowed image hosts are `7tv.app` and `7tvcdn.net` (enforced in utils).
- Conversion output is streamed (no on-disk storage by default).

## STYLE (FOLLOW)
- Imports: stdlib → third-party → local (`o7tv.*`), absolute imports only.
- Formatting: 4 spaces, 100-char lines, double quotes (Ruff).
- Types: annotate public functions; prefer PEP 604 unions (`Path | None`).
- Docstrings: Google style for public functions/classes.
- Errors: catch specific exceptions; use `HTTPException` for API errors; log unexpected errors.
- Templates: keep UI strings English-only; reuse existing Tailwind classes.

## ANTI-PATTERNS (THIS PROJECT)
- Do not bypass `ensure_allowed_image_url` or accept non-7tv hosts.
- Do not write converted files to disk unless docs are updated accordingly.
- Do not edit `uv.lock` by hand; use `uv add/remove` and `uv lock`.

## UNIQUE STYLES
- Base template provides `window.o7tv*` helpers and handles convert submits globally.
- UI uses Tailwind CDN + gradient buttons; reuse existing utility classes for parity.
- Infinite scroll expects `#search-grid`, `#static-grid`, and `#scroll-status` IDs with
  `data-page` and `data-query` attributes.

## COMMANDS
```bash
uv sync
uvicorn o7tv.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
python -m pytest tests/ -v
pre-commit run --all-files
docker build -t o7tv .
docker run -p 8000:8000 -v "$(pwd)/static:/app/static" o7tv
```

## NOTES
- `.vscode/launch.json` already uses `o7tv.main:app`; README/Dockerfile still mention
  `app.main:app` (update pending).
- No `tests/` directory exists yet; pytest commands are for future tests.
- `static/` is optional today because responses are streamed, but the Docker run
  command mounts it for future persistence.
