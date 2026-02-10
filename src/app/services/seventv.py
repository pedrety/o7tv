import requests

from app.config.config import settings

from ..models.emotes import EmoteImage, EmoteResult, EmoteSearchResponse


def _select_best_image(images: list[EmoteImage]) -> EmoteImage | None:
    """Selects the best image for conversion.

    Args:
        images (list[EmoteImage]): Available emote images.

    Returns:
        EmoteImage | None: The selected image or None if none available.
    """
    if not images:
        return None

    animated = [img for img in images if img.frame_count > 1]
    candidates = animated or images
    gif_candidates = [img for img in candidates if img.mime == "image/gif"]
    if gif_candidates:
        return max(
            gif_candidates, key=lambda img: (img.scale or 0, img.width, img.height)
        )
    return max(candidates, key=lambda img: (img.width, img.height))


def _select_png_x4(images: list[EmoteImage]) -> EmoteImage | None:
    """Select the x4 PNG image when available.

    Args:
        images (list[EmoteImage]): Available emote images.

    Returns:
        EmoteImage | None: The selected png image.
    """
    pngs = [img for img in images if img.mime == "image/png"]
    if not pngs:
        return None

    for img in pngs:
        if img.scale == 4:
            return img

    return max(pngs, key=lambda img: img.width)


def search_emotes(
    query: str | None,
    page: int = 1,
    per_page: int = 72,
    sort_by: str = "TOP_ALL_TIME",
    sort_order: str = "DESCENDING",
) -> EmoteSearchResponse:
    """Searches 7TV emotes by name.

    Args:
        query (str | None): The emote name query string.
        page (int): Page number to fetch.
        per_page (int): Number of results to return.
        sort_by (str): Sort field for results.
        sort_order (str): Sort order for results.

    Returns:
        EmoteSearchResponse: Paginated search results.

    Raises:
        requests.RequestException: If the API request fails.
        ValueError: If the API response is malformed.
    """
    gql_query = """
    query EmoteSearch(
      $query: String,
      $page: Int,
      $perPage: Int!,
      $sort: Sort!,
      $tags: [String!]!
    ) {
      emotes {
        search(
          query: $query
          page: $page
          perPage: $perPage
          sort: $sort
          tags: { tags: $tags, match: ANY }
          filters: {}
        ) {
          items {
            id
            defaultName
            images {
              url
              mime
              width
              height
              frameCount
              scale
            }
          }
          totalCount
          pageCount
        }
      }
    }
    """

    response = requests.post(
        settings.seventv_gql_url,
        json={
            "query": gql_query,
            "variables": {
                "query": query,
                "page": page,
                "perPage": per_page,
                "sort": {"sortBy": sort_by, "order": sort_order},
                "tags": [],
            },
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise ValueError("7TV search failed")

    search_payload = payload.get("data", {}).get("emotes", {}).get("search", {})
    items = search_payload.get("items", [])
    results: list[EmoteResult] = []
    for item in items:
        images = [
            EmoteImage(
                url=img["url"],
                mime=img["mime"],
                width=img["width"],
                height=img["height"],
                frame_count=img.get("frameCount", 1),
                scale=img.get("scale"),
            )
            for img in item.get("images", [])
            if "url" in img
        ]
        best = _select_best_image(images)
        static_png = _select_png_x4(images)
        results.append(
            EmoteResult(
                emote_id=item["id"],
                name=item["defaultName"],
                image=best,
                static_image=static_png,
                is_animated=any(img.frame_count > 1 for img in images),
            )
        )

    return EmoteSearchResponse(
        items=results,
        page_count=search_payload.get("pageCount", 0),
        total_count=search_payload.get("totalCount", 0),
    )
