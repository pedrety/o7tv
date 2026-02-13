import logging
from collections.abc import Iterator

import ffmpeg

logger = logging.getLogger(__name__)


def _raise_ffmpeg_error(stderr_msg: str) -> None:
    if (
        "Invalid data found when processing input" in stderr_msg
        or "image data not found" in stderr_msg
    ):
        raise RuntimeError(
            "The downloaded file appears to be corrupted or is not a valid video/GIF format. "
            "Try another emote URL."
        )
    if "Could not find codec parameters" in stderr_msg:
        raise RuntimeError(
            "Unable to recognize the file format. Make sure it is a valid GIF or video."
        )
    raise RuntimeError(f"Unable to convert the emote: {stderr_msg[:200]}")


def stream_webm(input_source: str) -> Iterator[bytes]:
    """Converts a media file to WebM format and yields the output as byte chunks.

    Args:
        input_source (str): Path or URL to the input media file.

    Returns:
        Iterator[bytes]: An iterator yielding chunks of the converted WebM data.

    Raises:
        RuntimeError: If ffmpeg conversion fails or streaming is not possible.
    """
    scale_w = "if(gt(iw,ih),512,trunc(512*iw/ih/2)*2)"
    scale_h = "if(gt(ih,iw),512,trunc(512*ih/iw/2)*2)"

    stream = ffmpeg.input(input_source).filter("scale", scale_w, scale_h)

    out_kwargs = {
        "vcodec": "libvpx-vp9",
        "pix_fmt": "yuva420p",
        "b:v": "0",
        "crf": 32,
        "auto-alt-ref": 0,
        "format": "webm",
        "t": 3,
    }

    process = (
        ffmpeg.output(stream, "pipe:", **out_kwargs)
        .overwrite_output()
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    try:
        if process.stdout is None:
            raise RuntimeError("Unable to stream the conversion output.")

        while True:
            chunk = process.stdout.read(8192)
            if not chunk:
                break
            yield chunk

        return_code = process.wait()
        if return_code != 0:
            stderr_msg = process.stderr.read().decode() if process.stderr else "unknown error"
            logger.error(f"FFmpeg conversion failed for {input_source}: {stderr_msg}")
            _raise_ffmpeg_error(stderr_msg)
    except GeneratorExit:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during streaming conversion of {input_source}: {e}")
        raise RuntimeError("Unexpected error during conversion.") from e
    finally:
        if process.poll() is None:
            process.kill()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
