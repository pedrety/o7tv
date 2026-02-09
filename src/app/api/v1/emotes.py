import tempfile
from pathlib import Path

import requests
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from app.core.config import STATIC_DIR, TEMPLATES
from app.services.conversion import convert_to_webm
from app.services.seventv import search_emotes
from app.utils.files import extract_emote_id
from app.utils.http import download_to_path

router = APIRouter()


@router.get("/")
async def index(request: Request) -> Response:
    """Render the main page with the form to submit an emote URL.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        TemplateResponse: The rendered HTML page with the form.
    """
    error_message = None
    try:
        trending = search_emotes(
            None,
            per_page=6,
            sort_by="TRENDING_DAILY",
        ).items
    except (ValueError, requests.RequestException):
        trending = []
        error_message = "No se pudo cargar el top de hoy"

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "emote_url": None,
            "search_results": None,
            "search_query": None,
            "trending_results": trending,
            "error": error_message,
        },
    )


@router.post("/convert")
async def convert(request: Request, emote_url: str = Form(...)) -> Response:
    """Handle the form submission to convert an emote URL to a webm file.

    Args:
        request (Request): The incoming HTTP request.
        emote_url (str): The URL of the emote to convert.

    Returns:
        TemplateResponse: The rendered HTML page with the conversion result or error message.
    """
    emote_id = extract_emote_id(emote_url)
    tmp_output = STATIC_DIR / f"{emote_id}.webm"

    if not tmp_output.exists():
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_input = Path(tmpdir) / f"emote_input-{emote_id}"
            downloaded = download_to_path(emote_url, tmp_input)
            if not downloaded:
                return TEMPLATES.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "error": "No se pudo descargar el emote desde la URL proporcionada",
                        "emote_url": None,
                        "search_results": None,
                        "search_query": None,
                    },
                )

            try:
                convert_to_webm(str(tmp_input), str(tmp_output))
            except RuntimeError as e:
                return TEMPLATES.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "error": str(e),
                        "emote_url": None,
                        "search_results": None,
                        "search_query": None,
                    },
                )

    ver = int(tmp_output.stat().st_mtime)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "emote_url": f"/static/{tmp_output.name}?v={ver}",
            "emote_file": tmp_output.name,
            "emote_name": emote_url,
            "search_results": None,
            "search_query": None,
        },
    )


@router.get("/search")
async def search(request: Request, q: str | None = None) -> Response:
    """Search emotes by name and render results.

    Args:
        request (Request): The incoming HTTP request.
        q (str | None): The emote name query.

    Returns:
        Response: The rendered HTML page with search results.
    """
    if not q or not q.strip():
        return await index(request)

    try:
        results = search_emotes(q)
    except (ValueError, requests.RequestException):
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "emote_url": None,
                "search_results": None,
                "search_query": q,
                "search_page": 1,
                "trending_results": [],
                "error": "No se pudo obtener resultados de búsqueda",
            },
        )

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "emote_url": None,
            "search_results": results.items,
            "search_query": q,
            "search_page": 1,
            "trending_results": [],
        },
    )


@router.get("/search/page")
async def search_page(q: str, page: int = 1) -> JSONResponse:
    """Return paginated search results for infinite scrolling.

    Args:
        q (str): The emote name query.
        page (int): Page number to fetch.

    Returns:
        JSONResponse: JSON payload with items and paging info.
    """
    try:
        results = search_emotes(q, page=page)
    except (ValueError, requests.RequestException) as exc:
        raise HTTPException(status_code=502, detail="Error consultando 7TV") from exc

    return JSONResponse(
        {
            "animated_items": [
                {
                    "id": item.emote_id,
                    "name": item.name,
                    "image_url": item.image.url if item.image else None,
                }
                for item in results.items
                if item.is_animated
            ],
            "static_items": [
                {
                    "id": item.emote_id,
                    "name": item.name,
                    "image_url": item.image.url if item.image else None,
                    "png_url": item.static_image.url if item.static_image else None,
                }
                for item in results.items
                if not item.is_animated
            ],
            "page": page,
            "page_count": results.page_count,
            "total_count": results.total_count,
        }
    )


@router.get("/download/{filename}")
async def download_file(filename: str) -> FileResponse:
    """Serve the converted webm file for download.

    Args:
        filename (str): The name of the file to download.

    Returns:
        FileResponse: The response containing the file for download.
    """
    path = Path(STATIC_DIR) / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(path, media_type="video/webm", filename="emote.webm")
