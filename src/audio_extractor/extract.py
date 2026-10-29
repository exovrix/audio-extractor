"""Core audio extraction API."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal

from audio_extractor.ffmpeg import find_ffmpeg

AudioFormat = Literal["wav", "flac", "mp3", "ogg"]

_FORMAT_CODECS: dict[str, list[str]] = {
    "wav": ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"],
    "mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
    "ogg": ["-c:a", "libvorbis", "-q:a", "5"],
}

_SUPPORTED_INPUT_SUFFIXES = {
    ".mp4",
    ".mov",
    ".webm",
    ".mkv",
    ".avi",
    ".m4a",
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".aac",
    ".wma",
}


def build_ffmpeg_args(
    input_path: Path,
    output_path: Path,
    *,
    format: AudioFormat = "wav",
    sample_rate: int = 16000,
    channels: int = 1,
    start: float | None = None,
    duration: float | None = None,
) -> list[str]:
    """Build an ffmpeg argument list for audio extraction/conversion.

    Does not invoke ffmpeg; useful for inspection and unit tests.
    """
    if format not in _FORMAT_CODECS:
        raise ValueError(
            f"Unsupported format {format!r}. Choose from: {', '.join(sorted(_FORMAT_CODECS))}."
        )
    if sample_rate <= 0:
        raise ValueError(f"sample_rate must be positive, got {sample_rate}")
    if channels < 1:
        raise ValueError(f"channels must be >= 1, got {channels}")
    if start is not None and start < 0:
        raise ValueError(f"start must be >= 0, got {start}")
    if duration is not None and duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    args: list[str] = ["-y", "-hide_banner", "-loglevel", "error"]
    if start is not None:
        args.extend(["-ss", str(start)])
    args.extend(["-i", str(input_path)])
    if duration is not None:
        args.extend(["-t", str(duration)])
    args.extend(["-vn", "-ac", str(channels), "-ar", str(sample_rate)])
    args.extend(_FORMAT_CODECS[format])
    args.append(str(output_path))
    return args


def extract(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    format: AudioFormat = "wav",
    sample_rate: int = 16000,
    channels: int = 1,
    start: float | None = None,
    duration: float | None = None,
) -> Path:
    """Extract or convert an audio track using ffmpeg.

    Args:
        input_path: Path to a video or audio file.
        output_path: Destination path. Defaults to ``<stem>.<format>`` beside the input.
        format: Output container/codec family: ``wav``, ``flac``, ``mp3``, or ``ogg``.
        sample_rate: Target sample rate in Hz (default 16000).
        channels: Number of audio channels (default 1 = mono).
        start: Optional start time in seconds.
        duration: Optional duration in seconds from ``start``.

    Returns:
        Path to the written audio file.

    Raises:
        FileNotFoundError: If ``input_path`` does not exist.
        ValueError: On invalid arguments.
        FFmpegNotFoundError: If ffmpeg is not on PATH.
        RuntimeError: If ffmpeg exits non-zero.
    """
    src = Path(input_path).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Input file not found: {src}")

    if output_path is None:
        dest = src.with_suffix(f".{format}")
    else:
        dest = Path(output_path).expanduser().resolve()
        if dest.suffix == "":
            dest = dest.with_suffix(f".{format}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = find_ffmpeg()
    args = build_ffmpeg_args(
        src,
        dest,
        format=format,
        sample_rate=sample_rate,
        channels=channels,
        start=start,
        duration=duration,
    )
    cmd = [ffmpeg, *args]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip() or "unknown ffmpeg error"
        raise RuntimeError(f"ffmpeg failed ({exc.returncode}): {detail}") from exc

    return dest
