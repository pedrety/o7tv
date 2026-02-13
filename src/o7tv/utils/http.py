import re
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
from fastapi import HTTPException


def download_to_path(emote_url: str, dest: Path) -> Path | None:
    """Downloads the emote from the URL to the destination; returns the Path if OK, None if fails.

    Args:
        emote_url (str): The URL of the emote to download.
        dest (Path): The destination path to save the downloaded emote.

    Returns:
        Path | None: The path to the downloaded emote, or None if the download failed
    """
    parsed = urlparse(emote_url)
    if parsed.scheme not in {"http", "https"}:
        return None

    response = requests.get(emote_url, timeout=15)
    if response.status_code != 200:
        return None

    dest.write_bytes(response.content)
    return dest


def ensure_allowed_image_url(image_url: str) -> str:
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


def resolve_emote_url(emote_url: str | None, emote_url_form: str | None) -> str:
    """Resolve an emote URL from query params or form data.

    Args:
        emote_url (str | None): The URL from query parameters.
        emote_url_form (str | None): The URL from form data.

    Returns:
        str: The resolved URL.

    Raises:
        HTTPException: If no URL is provided.
    """
    resolved = emote_url or emote_url_form
    if not resolved:
        raise HTTPException(status_code=422, detail="emote_url is required")
    return resolved


def safe_filename(name: str | None) -> str:
    """Create a safe WebM filename from the provided name.

    Args:
        name (str | None): The original emote name.

    Returns:
        str: A sanitized filename ending with .webm.
    """
    if not name:
        return "emote.webm"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", " ", name).strip()
    if not cleaned:
        cleaned = "emote"
    return f"{cleaned}.webm"


def content_disposition(filename: str, original_name: str | None) -> str:
    """Build a safe Content-Disposition header value.

    Args:
        filename (str): Safe filename for the download.
        original_name (str | None): Original name for UTF-8 filename.

    Returns:
        str: Content-Disposition header value.
    """
    quoted = original_name or filename
    cleaned = re.sub(r"[\r\n\"]+", "", quoted).strip()
    encoded = quote(cleaned)
    return f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded}"
