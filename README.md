# 🫡 TV

<div align="center">
  <img src="assets/icon.png" alt="o7tv icon" width="120" height="120">
</div>

FastAPI application that converts 7TV emote URLs to WebM files. It provides a
minimal web UI for searching emotes, converting them, and downloading the
converted output.

## Requirements

- Python 3.12+
- FFmpeg available in your PATH
- uv package manager

## Setup

Install dependencies:

```bash
uv sync
```

Optional environment configuration:

```bash
cp .env.example .env
```

## Run

Development server:

```bash
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

Production server:

```bash
uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 to use the UI.

## Docker

Build and run:

```bash
docker build -t o7tv .
docker run -p 8000:8000 -v "$(pwd)/static:/app/static" o7tv
```

Or with Docker Compose:

```bash
docker compose up --build
```

## Usage

- Use the search bar to find emotes or browse trending.
- Click Convert to generate a WebM file for an emote.
- Download the converted WebM or static PNG when available.

## Project structure

```
o7tv/
│
├── assets/               # Static assets like icons and images
├── static/               # Generated WebM files
├── src/
│   └── app/
│       ├── main.py       # FastAPI app factory
│       ├── api/          # HTTP routes and endpoints
│       ├── config/       # Configuration management
│       ├── models/       # Data models and schemas 
│       ├── services/     # Business logic and conversion pipeline
│       └── utils/        # Utility functions
├── templates/            # Jinja2 HTML templates
```

## Configuration

Configuration is handled through environment variables with the APP__ prefix.
See `.env.example` and `docs/configuration.md` for details.

## Documentation

Technical documentation is available in `docs/`:

- [`API details`](docs/api.md)
- [`Conversion pipeline details`](docs/conversion.md)
- [`Configuration settings`](docs/configuration.md)
- [`Error handling`](docs/errors.md)