"""Unit tests for audio_extractor (no real ffmpeg required for most cases)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from audio_extractor.extract import build_ffmpeg_args, extract
from audio_extractor.ffmpeg import FFmpegNotFoundError, clear_ffmpeg_cache, find_ffmpeg


def test_build_ffmpeg_args_defaults(tmp_path: Path) -> None:
    src = tmp_path / "in.mp4"
    dest = tmp_path / "out.wav"
    args = build_ffmpeg_args(src, dest)
    assert args[:4] == ["-y", "-hide_banner", "-loglevel", "error"]
    assert "-i" in args and str(src) in args
    assert "-vn" in args
    assert args[args.index("-ac") + 1] == "1"
    assert args[args.index("-ar") + 1] == "16000"
    assert "-c:a" in args and "pcm_s16le" in args
    assert args[-1] == str(dest)


def test_build_ffmpeg_args_with_trim_and_mp3(tmp_path: Path) -> None:
    src = tmp_path / "in.mkv"
    dest = tmp_path / "out.mp3"
    args = build_ffmpeg_args(
        src,
        dest,
        format="mp3",
        sample_rate=44100,
        channels=2,
        start=1.5,
        duration=3.0,
    )
    assert args[args.index("-ss") + 1] == "1.5"
    assert args[args.index("-t") + 1] == "3.0"
    assert args[args.index("-ar") + 1] == "44100"
    assert args[args.index("-ac") + 1] == "2"
    assert "libmp3lame" in args


def test_build_ffmpeg_args_rejects_bad_format(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported format"):
        build_ffmpeg_args(tmp_path / "a.mp4", tmp_path / "b.wav", format="aac")  # type: ignore[arg-type]


def test_build_ffmpeg_args_rejects_bad_rate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="sample_rate"):
        build_ffmpeg_args(tmp_path / "a.mp4", tmp_path / "b.wav", sample_rate=0)


def test_extract_missing_input(tmp_path: Path) -> None:
    missing = tmp_path / "nope.mp4"
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        extract(missing)


def test_extract_invokes_ffmpeg(tmp_path: Path) -> None:
    src = tmp_path / "clip.mp4"
    src.write_bytes(b"fake")
    dest = tmp_path / "out.wav"

    def fake_run(cmd, check=True, capture_output=True, text=True):
        Path(cmd[-1]).write_bytes(b"RIFF")
        return MagicMock(returncode=0)

    with (
        patch("audio_extractor.extract.find_ffmpeg", return_value="/usr/bin/ffmpeg"),
        patch("audio_extractor.extract.subprocess.run", side_effect=fake_run) as run_mock,
    ):
        result = extract(src, dest, format="wav", sample_rate=16000, channels=1)

    assert result == dest.resolve()
    run_mock.assert_called_once()
    cmd = run_mock.call_args.args[0]
    assert cmd[0] == "/usr/bin/ffmpeg"
    assert str(src.resolve()) in cmd
    assert str(dest.resolve()) in cmd


def test_find_ffmpeg_missing() -> None:
    clear_ffmpeg_cache()
    with patch("audio_extractor.ffmpeg.shutil.which", return_value=None):
        with pytest.raises(FFmpegNotFoundError, match="ffmpeg not found"):
            find_ffmpeg()
    clear_ffmpeg_cache()


@pytest.mark.skipif(
    __import__("shutil").which("ffmpeg") is None,
    reason="ffmpeg not on PATH",
)
def test_real_ffmpeg_available() -> None:
    path = find_ffmpeg()
    assert Path(path).exists()
