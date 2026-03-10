# Conversion Pipeline

The conversion pipeline converts a 7TV emote asset into a WebM response using
`ffmpeg`. The process is implemented in
`src/o7tv/services/conversion.py` and shared URL helpers in
`src/o7tv/utils/http.py`.

## Steps

1. **URL validation**
   - The emote URL must use http/https and be hosted on `7tv.app` or
     `7tvcdn.net`.

2. **Scaling**
   - The video is scaled to fit inside a 512x512 bounding box.
   - The aspect ratio is preserved using ffmpeg conditional expressions.

3. **Encoding**
   - Codec: `libvpx-vp9`
   - Pixel format: `yuva420p` for transparency support
   - CRF: `32`
   - `auto-alt-ref` disabled
   - Output is trimmed to 3 seconds.
   - When `APP__MAX_WEBM_SIZE_BYTES` is configured, ffmpeg applies a target bitrate
     and a hard output cap (`-fs`) so generated WebM output stays within that limit.

## Output

- Converted files are returned directly in the HTTP response without static storage.
- When a size limit is configured, the service buffers the generated WebM in memory
  so it can verify the final payload size before sending it.

## Error handling

The converter raises descriptive errors for common ffmpeg failures, including
corrupted inputs and unsupported formats. Unexpected failures are logged and
surface a generic conversion error message.
