# Agent Guidelines for o7tv

## Project Overview
Python 3.12+ FastAPI app that converts 7TV emotes to WebM. Uses `uv` for
dependency management; templates live in `templates/` and static outputs in
`static/`.

## Environment Requirements
- Python >= 3.12
- FFmpeg installed on the system
- `uv` package manager

## Build, Run, Lint, and Test Commands

### Install / Sync Dependencies
```bash
uv sync
```

### Run the App
```bash
# Dev server (reload)
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000

# Run via python module
python -m uvicorn app.main:app --app-dir src --reload
```

### Docker
```bash
docker build -t o7tv .
docker run -p 8000:8000 -v "$(pwd)/static:/app/static" o7tv
docker compose up --build
```

### Tests
**Note:** No `tests/` directory exists in this repo. If tests are added, use
pytest:
```bash
# Run all tests
python -m pytest tests/ -v

# Run a single test by name or pattern
python -m pytest tests/ -k "test_name" -v

# Run a single test file
python -m pytest tests/test_emotes.py -v
```

### Lint / Format / Type Check
Pre-commit is the source of truth.
```bash
# Install hooks (once)
pre-commit install

# Run all hooks
pre-commit run --all-files

# Individual tools (if installed)
python -m ruff check src/
python -m ruff format src/
mypy src/
```

### Tooling Notes
- No CI workflows are present in `.github/workflows/`.
- Use `uv sync` for dependency installs (`uv.lock` is committed).

## Pre-commit Hooks (Configured)
Defined in `.pre-commit-config.yaml`:
- `pyupgrade`
- `mypy`
- `ruff` (with `--fix`)
- `ruff-format`
- Standard pre-commit hooks (trailing whitespace, TOML/YAML checks, etc.)

## Code Style Guidelines

### Imports
- Group imports: stdlib → third-party → local (`o7tv.*`).
- Use absolute imports (e.g., `from o7tv.api.v1.emotes import router`).
- One import per line; alphabetize within groups.

### Formatting
- 4-space indentation.
- Prefer double quotes for strings.
- Line length: 100 (Ruff configured).

### Types
- Annotate all function signatures.
- Use PEP 604 unions (`Path | None`) over `Optional[Path]`.

### Naming
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Private helpers: prefix `_`.

### Docstrings
- Use Google-style docstrings with Args/Returns/Raises.
- Document public functions and classes.

### Error Handling
- Catch specific exceptions (avoid bare `except:`).
- Use `HTTPException` for API error responses.
- Log unexpected errors (see `services/conversion.py`).

### Jinja/Frontend
- Templates are Jinja2 in `templates/` with inline CSS in `templates/base.html`.
- Keep UI strings consistent and English-only.

## Architecture & Structure
- `src/o7tv/main.py` → FastAPI app factory
- `src/o7tv/api/v1/` → API routes
- `src/o7tv/services/` → business logic
- `src/o7tv/utils/` → helpers (HTTP, file utilities)
- `src/o7tv/models/` → Pydantic models
- `templates/` → Jinja2 templates
- `static/` → generated WebM outputs

## Dependency Management
- Source of truth: `pyproject.toml` + `uv.lock`.
- Use `uv add/remove` for dependencies; `uv lock` to update.

## Configuration & Debugging
- VSCode launch: `.vscode/launch.json` (uvicorn, reload, `--app-dir src`).
- Config lives in `src/o7tv/config/config.py` using `pydantic-settings`.

## Cursor / Copilot Rules
- No `.cursorrules` or `.cursor/rules` present.
- No `.github/copilot-instructions.md` present.

## Common Tasks
- Add new endpoint: create route in `src/o7tv/api/v1/emotes.py`.
- Add utility: `src/o7tv/utils/*.py` with type hints + docstring.
- Update templates: `templates/*.html` and pass data via `TemplateResponse`.
