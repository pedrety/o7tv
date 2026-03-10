import logging

import ffmpeg

from o7tv.exceptions.ffmpeg_exceptions import (
    FfmpegConversionError,
    FfmpegError,
    FfmpegInvalidInputError,
    FfmpegStreamError,
    FfmpegUnsupportedFormatError,
)

logger = logging.getLogger(__name__)


def _raise_ffmpeg_error(stderr_msg: str) -> None:
    if (
        "Invalid data found when processing input" in stderr_msg
        or "image data not found" in stderr_msg
    ):
        raise FfmpegInvalidInputError(
            "The downloaded file appears to be corrupted or is not a valid video/GIF format. "
            "Try another emote URL."
        )
    if "Could not find codec parameters" in stderr_msg:
        raise FfmpegUnsupportedFormatError(
            "Unable to recognize the file format. Make sure it is a valid GIF or video."
        )
    raise FfmpegConversionError(f"Unable to convert the emote: {stderr_msg[:200]}")


def _build_scaled_stream(input_source: str, max_side: int) -> ffmpeg.nodes.FilterableStream:
    scale_w = f"if(gt(iw,ih),{max_side},trunc({max_side}*iw/ih/2)*2)"
    scale_h = f"if(gt(ih,iw),{max_side},trunc({max_side}*ih/iw/2)*2)"
    return ffmpeg.input(input_source).filter("scale", scale_w, scale_h)


def _encode_webm_bytes(input_source: str, *, crf: int, fs_limit: int | None) -> bytes:
    stream = _build_scaled_stream(input_source, 512)

    out_kwargs: dict[str, int | str] = {
        "vcodec": "libvpx-vp9",
        "pix_fmt": "yuva420p",
        "b:v": "0",
        "crf": crf,
        "auto-alt-ref": 0,
        "format": "webm",
        "t": 3,
    }

    if fs_limit is not None:
        duration_seconds = 3
        target_bitrate_bps = max(int((fs_limit * 8) / duration_seconds * 0.92), 24_000)
        out_kwargs["b:v"] = target_bitrate_bps
        out_kwargs["maxrate"] = target_bitrate_bps
        out_kwargs["bufsize"] = target_bitrate_bps * 2
        out_kwargs["fs"] = fs_limit

    process = (
        ffmpeg.output(stream, "pipe:", **out_kwargs)
        .overwrite_output()
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    try:
        output, stderr = process.communicate()
        if process.returncode != 0:
            stderr_msg = stderr.decode() if stderr else "unknown error"
            logger.error(f"FFmpeg conversion failed for {input_source}: {stderr_msg}")
            _raise_ffmpeg_error(stderr_msg)
        return bytes(output or b"")
    finally:
        if process.poll() is None:
            process.kill()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()


def render_webm_bytes(input_source: str, max_output_bytes: int | None = None) -> bytes:
    """Converts a media file to WebM format and returns the output as bytes.

    Args:
        input_source (str): Path or URL to the input media file.
        max_output_bytes (int | None): Maximum allowed WebM output size in bytes.

    Returns:
        bytes: The converted WebM payload.

    Raises:
        FfmpegError: If ffmpeg conversion fails or the size limit cannot be met.
    """
    try:
        if max_output_bytes is None:
            return _encode_webm_bytes(input_source, crf=32, fs_limit=None)

        attempts = [32, 36, 40, 44, 48, 52, 56, 60, 63]
        last_payload = b""

        for crf in attempts:
            fs_limit = max(max_output_bytes - 1024, 1024)
            payload = _encode_webm_bytes(
                input_source,
                crf=crf,
                fs_limit=fs_limit,
            )
            last_payload = payload
            if len(payload) <= max_output_bytes:
                return payload

        if not last_payload:
            raise FfmpegStreamError("Unable to stream the conversion output.")
        raise FfmpegConversionError(
            f"Unable to fit output within {max_output_bytes} bytes after quality reduction. "
            f"Smallest result was {len(last_payload)} bytes."
        )
    except FfmpegError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during streaming conversion of {input_source}: {e}")
        raise FfmpegConversionError("Unexpected error during conversion.") from e
