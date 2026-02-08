# Agent Guidelines for 7tv-to-sticker

## Project Overview
This is a Python 3.12+ FastAPI application that converts 7TV emotes to WebM sticker format. The project uses `uv` for dependency management.

## Environment Setup

### Requirements
- Python ≥ 3.12
- FFmpeg (system package)
- uv package manager

### Installation
```bash
uv sync  # Install dependencies from uv.lock
```

## Build, Lint, and Test Commands

### Running the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000

# Using Python module
python -m uvicorn app.main:app --app-dir src --reload
```

### Testing
```bash
# Run all tests
python test.py

# Run specific test (pattern-based)
python -m pytest tests/ -k "test_name" -v

# Test with coverage
python -m pytest --cov=src --cov-report=html
```

### Linting and Type Checking
```bash
# Format code (using black style if added)
python -m black src/

# Check types with pyright/pyright via IDE
pyright src/

# Check imports with isort
python -m isort src/

# Lint with ruff (if configured)
python -m ruff check src/
```

**Note:** The project currently has no formal linting/formatting tools configured. Use this as a reference for future setup.

## Code Style Guidelines

### Imports
- Group imports in this order:
  1. Standard library (pathlib, asyncio, tempfile, etc.)
  2. Third-party (fastapi, ffmpeg, requests, pydantic, etc.)
  3. Local application (from app.*)
- Use absolute imports (prefer `from app.core.config import TEMPLATES` over relative imports)
- One import per line for clarity
- Sort within each group alphabetically
- **Example:** See src/app/api/v1/emotes.py and src/app/utils/http.py

### Formatting
- **Line length:** 88 characters (Black default)
- **Indentation:** 4 spaces
- **Strings:** Use double quotes (`"`)
- **Type hints:** Always include return types and parameter types (PEP 484)

### Type Hints and Types
- Use modern union syntax: `Path | None` (Python 3.10+) instead of `Optional[Path]`
- Provide complete type annotations on all function signatures
- Use `typing.Union` only when necessary for complex types
- Example: `def download_to_path(emote_url: str, dest: Path) -> Path | None:`

### Naming Conventions
- **Functions/Variables:** `snake_case` (e.g., `extract_emote_id`, `convert_to_webm`)
- **Classes:** `PascalCase` (e.g., `Settings`, `HTTPException`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `STATIC_DIR`, `STATIC_URL`)
- **Private methods:** prefix with `_` (e.g., `_internal_helper()`)
- **Module names:** `lowercase_with_underscores`

### Documentation
- **Docstrings:** Use Google-style format for all functions and classes
- Include Args, Returns, and Raises sections
- **Example:**
  ```python
  def convert_to_webm(input_file: str, output_file: str) -> None:
      """Converts a media file to WebM format, scaling and adjusting speed.
      
      Args:
          input_file (str): Path to the input media file.
          output_file (str): Path to save the converted WebM file.
      """
  ```

### Error Handling
- Explicitly catch specific exceptions, not bare `except:`
- **Example:** `except (ValueError, IndexError): pass`
- Use FastAPI's `HTTPException` for API errors (see src/app/api/v1/emotes.py:62)
- Return meaningful error messages when possible
- Log or raise exceptions appropriately (currently minimal logging)

### Architecture & Structure
- **Config:** Use Pydantic `BaseSettings` (src/app/core/config.py)
- **API Routes:** Define in src/app/api/ with versioning (v1, v2, etc.)
- **Services:** Business logic in src/app/services/
- **Utils:** Helper functions in src/app/utils/ organized by concern (http.py, files.py)
- **Models:** Data models in src/app/models/ (currently minimal)

### FastAPI Specifics
- Use path parameters for REST endpoints: `@router.get("/download/{filename}")`
- Use Form parameters for form submissions: `emote_url: str = Form(...)`
- Return `TemplateResponse` for HTML responses (Jinja2 integration)
- Use `FileResponse` for file downloads
- Raise `HTTPException` with appropriate status codes (404, 400, etc.)
- Async functions recommended for I/O operations

### Best Practices
- Avoid broad exception handling; be specific
- Use context managers (`with` statements) for resource management
- Validate file paths and URLs before processing
- Handle `Path` objects from `pathlib` instead of strings where possible
- Use descriptive variable names that reflect intent
- Keep functions focused on single responsibility

## Project Dependencies
- **fastapi:** Web framework
- **uvicorn:** ASGI server
- **ffmpeg-python:** Video encoding
- **requests:** HTTP client
- **pydantic:** Data validation and settings
- **jinja2:** Template rendering
- **gql:** GraphQL client (for potential emote API queries)

## File Organization
```
src/app/
├── __init__.py
├── main.py           # FastAPI app factory
├── core/
│   ├── config.py     # Configuration (paths, settings)
│   └── __init__.py
├── api/
│   ├── v1/
│   │   ├── emotes.py # Emote conversion endpoints
│   │   └── __init__.py
│   └── __init__.py
├── services/
│   ├── conversion.py # FFmpeg conversion logic
│   └── __init__.py
├── utils/
│   ├── http.py       # HTTP utilities (download)
│   ├── files.py      # File utilities (extraction)
│   └── __init__.py
├── models/           # Pydantic models (empty)
├── static/           # Converted WebM files
└── templates/        # Jinja2 HTML templates
```

## PYTHONPATH
The project sets `PYTHONPATH=/app/src` in Docker. Ensure imports work with:
```python
from app.core.config import Settings
from app.api.v1.emotes import router
```

## Common Tasks
- **Add new endpoint:** Create route in src/app/api/v1/emotes.py, use `@router.get()` or `@router.post()`
- **Add utility:** Create function in src/app/utils/ with proper docstring and type hints
- **Add service logic:** Create function in src/app/services/ for reusable business logic
- **Modify settings:** Update src/app/core/config.py using Pydantic BaseSettings
- **Update templates:** Modify files in src/templates/ and pass variables via TemplateResponse context
