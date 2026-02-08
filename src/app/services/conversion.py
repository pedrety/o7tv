import ffmpeg


def get_duration(path: str) -> float | None:
    """Obtains the duration of a media file in seconds; None if unknown.

    Args:
        path (str): Path to the media file.

    Returns:
        float | None: Duration in seconds, or None if not available.
    """
    try:
        probe = ffmpeg.probe(path)
        fmt = probe.get("format", {})
        if fmt.get("duration"):
            return float(fmt["duration"])
        for stream in probe.get("streams", []):
            if stream.get("duration"):
                return float(stream["duration"])
    except Exception:
        return None
    return None


def convert_to_webm(input_file: str, output_file: str) -> None:
    """Converts a media file to WebM format, scaling and adjusting speed as needed.

    Args:
        input_file (str): Path to the input media file.
        output_file (str): Path to save the converted WebM file.
    """
    duration = get_duration(input_file)
    speed_factor = duration / 3.0 if duration and duration > 3.0 else None

    scale_w = "if(gt(iw,ih),512,trunc(512*iw/ih/2)*2)"
    scale_h = "if(gt(ih,iw),512,trunc(512*ih/iw/2)*2)"

    stream = ffmpeg.input(input_file).filter("scale", scale_w, scale_h)

    if speed_factor:
        stream = stream.filter("setpts", f"PTS/{speed_factor}")

    out_kwargs = {
        "vcodec": "libvpx-vp9",
        "pix_fmt": "yuva420p",
        **{"b:v": "0"},
        "crf": 32,
        **{"auto-alt-ref": 0},
    }

    # Enforce máximo 3s si no hay duración conocida o para redondeo del speedup.
    if speed_factor or duration is None or duration > 3.0:
        out_kwargs["t"] = 3

    ffmpeg.output(stream, output_file, **out_kwargs).overwrite_output().run(quiet=True)
