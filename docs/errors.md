# Error Handling

This document summarizes user-facing error behavior as implemented in
`src/app/api/v1/emotes.py` and `src/app/services/conversion.py`.

## HTTP errors

| Endpoint | Status | Condition |
| --- | --- | --- |
| `/download/{filename}` | 404 | File not found in `static/`. |
| `/download-image` | 400 | Invalid URL scheme or host not allowed. |
| `/download-image` | 502 | Upstream image download failed. |
| `/search/page` | 502 | Upstream 7TV query failed. |

## Conversion errors

Conversion failures are surfaced in the UI with descriptive messages, including
cases where the input file is corrupted, the media format is unrecognized, or
ffmpeg returns a general error. Unexpected exceptions are logged and displayed
as a generic conversion failure.
