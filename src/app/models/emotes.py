from pydantic import BaseModel


class EmoteImage(BaseModel):
    """Represents a 7TV emote image.

    Args:
        url (str): The image URL.
        mime (str): The MIME type of the image.
        width (int): The image width in pixels.
        height (int): The image height in pixels.
        frame_count (int): Number of frames for animated images.
        scale (int | None): Image scale (1-4).
    """

    url: str
    mime: str
    width: int
    height: int
    frame_count: int
    scale: int | None


class EmoteResult(BaseModel):
    """Represents a 7TV emote search result.

    Args:
        emote_id (str): The 7TV emote ID.
        name (str): The emote default name.
        image (EmoteImage | None): The selected preview image.
        static_image (EmoteImage | None): The png x4 static image.
        is_animated (bool): Whether the emote is animated.
    """

    emote_id: str
    name: str
    image: EmoteImage | None
    static_image: EmoteImage | None
    is_animated: bool


class EmoteSearchResponse(BaseModel):
    """Represents a paginated emote search response.

    Args:
        items (list[EmoteResult]): Search results.
        page_count (int): Total number of pages.
        total_count (int): Total number of results.
    """

    items: list[EmoteResult]
    page_count: int
    total_count: int
