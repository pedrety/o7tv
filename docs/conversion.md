# Conversion Pipeline

The conversion pipeline downloads a 7TV emote asset and encodes it into a WebM
file using `ffmpeg`. The process is implemented in
`src/app/services/conversion.py` and uses helpers from `src/app/utils/`.

## Steps

1. **Emote ID extraction**
   - The emote ID is derived from the URL path segment following `/emote/`.
   - If the ID cannot be extracted, a UUID-based filename is used.

2. **Download source asset**
   - The emote URL is downloaded with a 15-second timeout.
   - Non-200 responses or invalid URL schemes fail the download step.

3. **Probe duration**
   - ffmpeg probes the input to determine duration.
   - If the duration exceeds 3 seconds, the output is sped up to fit within
     3 seconds.

4. **Scaling**
   - The video is scaled to fit inside a 512x512 bounding box.
   - The aspect ratio is preserved using ffmpeg conditional expressions.

5. **Encoding**
   - Codec: `libvpx-vp9`
   - Pixel format: `yuva420p` for transparency support
   - CRF: `32`
   - `auto-alt-ref` disabled
   - Output is trimmed to 3 seconds when duration is unknown or too long.

## Output

- Converted files are saved to the static directory as `<emote_id>.webm`.
- The UI links to `/static/<emote_id>.webm?v=<mtime>` to ensure cache-busting.

## Error handling

The converter raises descriptive errors for common ffmpeg failures, including
corrupted inputs and unsupported formats. Unexpected failures are logged and
surface a generic conversion error message.
