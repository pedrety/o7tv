from urllib.parse import urlparse
from uuid import uuid4


def extract_emote_id(emote_url: str) -> str:
    """Extracts the emote ID from a 7TV emote URL.

    Format: https://cdn.7tv.app/emote/01F6MQ33FG000FFJ97ZB8MWV52/4x.avif

    Args:
        emote_url (str): The URL of the emote.

    Returns:
        str: The extracted emote ID, or a unique identifier if extraction fails.
    """
    parsed = urlparse(emote_url)
    parts = [p for p in parsed.path.split("/") if p]
    try:
        idx = parts.index("emote")
        candidate = parts[idx + 1]
        if candidate.isalnum():
            return candidate

    except (ValueError, IndexError):
        pass

    return uuid4().hex
