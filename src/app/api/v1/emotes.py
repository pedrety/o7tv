import tempfile
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response

from app.core.config import STATIC_DIR, TEMPLATES
from app.services.conversion import convert_to_webm
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
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "emote_url": None},
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
                    },
                )

            convert_to_webm(str(tmp_input), str(tmp_output))

    ver = int(tmp_output.stat().st_mtime)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "emote_url": f"/static/{tmp_output.name}?v={ver}",
            "emote_file": tmp_output.name,
            "emote_name": emote_url,
        },
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
