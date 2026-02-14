# Error Handling

This document summarizes user-facing error behavior as implemented in
`src/o7tv/api/emotes.py` and `src/o7tv/services/conversion.py`.

## HTTP errors

| Endpoint | Status | Condition |
| --- | --- | --- |
| `/download-image` | 400 | Invalid URL scheme or host not allowed. |
| `/download-image` | 502 | Upstream image download failed. |
| `/search/page` | 502 | Upstream 7TV query failed. |
| `/convert/download` | 422 | Missing required `emote_url`. |

## Conversion errors

Conversion failures are surfaced in the UI with descriptive messages, including
cases where the input file is corrupted, the media format is unrecognized, or
ffmpeg returns a general error. Unexpected exceptions are logged and displayed
as a generic conversion failure.
