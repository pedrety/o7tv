from pathlib import Path
from urllib.parse import urlparse

import requests


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
