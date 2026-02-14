# API Documentation

All endpoints are defined in `src/o7tv/api/emotes.py` and are mounted at the
root path.

## GET /

Renders the main UI with trending emotes.

**Query parameters**
- `sort` (string, optional): One of `TOP_ALL_TIME`, `TRENDING_DAILY`,
  `UPLOAD_DATE`. Invalid values fall back to `TOP_ALL_TIME`.

**Behavior**
- Calls `search_emotes(None, per_page=9, sort_by=sort)` to populate trending
  results.
- Renders `templates/home.html`.

## POST /convert/download

Converts a 7TV emote URL into a WebM stream and triggers a download.

**Form fields**
- `emote_url` (string, required): Direct URL to the emote image.
- `emote_name` (string, optional): Emote display name used for the filename.

**Behavior**
- Validates the emote URL host (`7tv.app`, `7tvcdn.net`).
- Streams the WebM conversion output (no static file storage).
- Uses `Content-Disposition` to suggest a filename based on `emote_name`.

## GET /search

Searches 7TV emotes by name and renders results.

**Query parameters**
- `emote_name` (string, optional): Search query. Blank values return the index page.

**Behavior**
- Calls `search_emotes(emote_name)`.
- Renders `templates/results.html`.

**Failure cases**
- On upstream errors, renders `results.html` with an error message.

## GET /search/page

Returns a JSON payload for infinite scrolling.

**Query parameters**
- `emote_name` (string, required): Search query.
- `page` (integer, optional): Page number, defaults to 1.

**Response JSON**
```json
{
  "animated_items": [
    {"id": "...", "name": "...", "image_url": "..."}
  ],
  "static_items": [
    {"id": "...", "name": "...", "image_url": "...", "png_url": "..."}
  ],
  "page": 1,
  "page_count": 10,
  "total_count": 100
}
```

**Failure cases**
- Returns HTTP 502 if the upstream 7TV request fails.


## GET /download-image

Proxy-downloads an image to force a file download from the browser.

**Query parameters**
- `url` (string, required): Image URL. Must use http/https and be hosted on
  `7tv.app` or `7tvcdn.net`.

**Failure cases**
- Returns HTTP 400 for invalid or disallowed hosts.
- Returns HTTP 502 if the upstream download fails.
