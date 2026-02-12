# API Documentation

All endpoints are defined in `src/app/api/v1/emotes.py` and are mounted at the
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

## POST /convert

Converts a 7TV emote URL into a WebM file and renders the conversion result.

**Form fields**
- `emote_url` (string, required): Direct URL to the emote image.

**Behavior**
- Extracts the emote ID from the URL to derive the output filename.
- Downloads the emote into a temporary directory.
- Converts the file to WebM and stores it in `static/`.
- Renders `templates/convert.html` with the generated WebM URL.

**Failure cases**
- If the download fails, renders a template error message.
- If conversion fails, renders the error message raised by the converter.

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

## GET /download/{filename}

Downloads a converted WebM file from the static directory.

**Path parameters**
- `filename` (string): Name of the WebM file in `static/`.

**Failure cases**
- Returns HTTP 404 if the file does not exist.

## GET /download-image

Proxy-downloads an image to force a file download from the browser.

**Query parameters**
- `url` (string, required): Image URL. Must use http/https and be hosted on
  `7tv.app` or `7tvcdn.net`.

**Failure cases**
- Returns HTTP 400 for invalid or disallowed hosts.
- Returns HTTP 502 if the upstream download fails.
