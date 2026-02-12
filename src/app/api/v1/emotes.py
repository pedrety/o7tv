import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from app.config.config import settings
from app.services.conversion import convert_to_webm
from app.services.seventv import search_emotes
from app.utils.files import extract_emote_id
from app.utils.http import download_to_path

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _ensure_allowed_image_url(image_url: str) -> str:
    """Validate image URL for download proxy.

    Args:
        image_url (str): The image URL to validate.

    Returns:
        str: The validated URL.

    Raises:
        HTTPException: If the URL is invalid or not allowed.
    """
    parsed = urlparse(image_url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Invalid URL")

    hostname = (parsed.hostname or "").lower()
    if not (hostname.endswith("7tv.app") or hostname.endswith("7tvcdn.net")):
        raise HTTPException(status_code=400, detail="Host not allowed")

    return image_url


@router.get("/")
async def index(request: Request, sort: str = "TOP_ALL_TIME") -> Response:
    """Render the main page with the form to submit an emote URL.

    Args:
        request (Request): The incoming HTTP request.
        sort (str): Sort type for emotes (TOP_ALL_TIME, TRENDING_DAILY, NEW).

    Returns:
        TemplateResponse: The rendered HTML page with the form.
    """
    error_message = None
    trending = []

    # Validate sort parameter
    valid_sorts = ["TOP_ALL_TIME", "TRENDING_DAILY", "UPLOAD_DATE"]
    if sort not in valid_sorts:
        sort = "TOP_ALL_TIME"

    try:
        trending = search_emotes(
            None,
            per_page=9,
            sort_by=sort,
        ).items
    except (ValueError, requests.RequestException):
        error_message = "Unable to load emotes"

    return templates.TemplateResponse(
        "home.html",
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
    tmp_output = settings.static_dir / f"{emote_id}.webm"

    if not tmp_output.exists():
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_input = Path(tmpdir) / f"emote_input-{emote_id}"
            downloaded = download_to_path(emote_url, tmp_input)
            if not downloaded:
                return templates.TemplateResponse(
                    "convert.html",
                    {
                        "request": request,
                        "error": "Unable to download the emote from the provided URL",
                        "emote_url": None,
                        "search_results": None,
                        "search_query": None,
                        "trending_results": [],
                    },
                )

            try:
                convert_to_webm(str(tmp_input), str(tmp_output))
            except RuntimeError as e:
                return templates.TemplateResponse(
                    "convert.html",
                    {
                        "request": request,
                        "error": str(e),
                        "emote_url": None,
                        "search_results": None,
                        "search_query": None,
                        "trending_results": [],
                    },
                )

    ver = int(tmp_output.stat().st_mtime)
    return templates.TemplateResponse(
        "convert.html",
        {
            "request": request,
            "emote_url": f"/static/{tmp_output.name}?v={ver}",
            "emote_file": tmp_output.name,
            "emote_name": emote_url,
            "search_results": None,
            "search_query": None,
            "trending_results": [],
        },
    )


@router.get("/search")
async def search(request: Request, emote_name: str | None = None) -> Response:
    """Search emotes by name and render results.

    Args:
        request (Request): The incoming HTTP request.
        emote_name (str | None): The emote name query.

    Returns:
        Response: The rendered HTML page with search results.
    """
    if not emote_name or not emote_name.strip():
        return await index(request)

    try:
        results = search_emotes(emote_name)
    except (ValueError, requests.RequestException):
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "emote_url": None,
                "search_results": None,
                "search_query": emote_name,
                "search_page": 1,
                "trending_results": [],
                "error": "Unable to fetch search results",
            },
        )

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "emote_url": None,
            "search_results": results.items,
            "search_query": emote_name,
            "search_page": 1,
            "trending_results": [],
        },
    )


@router.get("/search/page")
async def search_page(emote_name: str, page: int = 1) -> JSONResponse:
    """Return paginated search results for infinite scrolling.

    Args:
        emote_name (str): The emote name query.
        page (int): Page number to fetch.

    Returns:
        JSONResponse: JSON payload with items and paging info.
    """
    try:
        results = search_emotes(emote_name, page=page)
    except (ValueError, requests.RequestException) as exc:
        raise HTTPException(status_code=502, detail="Error querying 7TV") from exc

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
    path = settings.static_dir / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="video/webm", filename="emote.webm")


@router.get("/download-image")
async def download_image(url: str) -> Response:
    """Proxy-download an external image so the browser forces download.

    Args:
        url (str): The image URL to download.

    Returns:
        Response: The response containing the image content.
    """
    image_url = _ensure_allowed_image_url(url)
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Error downloading image") from exc

    content_type = response.headers.get("Content-Type", "application/octet-stream")
    filename = Path(urlparse(image_url).path).name or "emote"
    filename = unquote(filename)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=response.content, media_type=content_type, headers=headers)
