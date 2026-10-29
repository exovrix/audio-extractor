"""Locate ffmpeg and ffprobe on PATH."""

from __future__ import annotations

import shutil
from functools import lru_cache


class FFmpegNotFoundError(RuntimeError):
    """Raised when ffmpeg or ffprobe cannot be found on PATH."""


@lru_cache(maxsize=1)
def find_ffmpeg() -> str:
    """Return the path to the ``ffmpeg`` executable.

    Raises:
        FFmpegNotFoundError: If ``ffmpeg`` is not on ``PATH``.
    """
    path = shutil.which("ffmpeg")
    if path is None:
        raise FFmpegNotFoundError(
            "ffmpeg not found on PATH. Install ffmpeg and ensure it is available "
            "in your environment (e.g. apt install ffmpeg, brew install ffmpeg, "
            "or WinGet on Windows)."
        )
    return path


@lru_cache(maxsize=1)
def find_ffprobe() -> str:
    """Return the path to the ``ffprobe`` executable.

    Raises:
        FFmpegNotFoundError: If ``ffprobe`` is not on ``PATH``.
    """
    path = shutil.which("ffprobe")
    if path is None:
        raise FFmpegNotFoundError(
            "ffprobe not found on PATH. Install ffmpeg (which includes ffprobe) "
            "and ensure it is available in your environment."
        )
    return path


def clear_ffmpeg_cache() -> None:
    """Clear cached ffmpeg/ffprobe paths (useful in tests)."""
    find_ffmpeg.cache_clear()
    find_ffprobe.cache_clear()
