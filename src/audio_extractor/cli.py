"""Command-line interface for audio-extractor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from audio_extractor import __version__, extract
from audio_extractor.ffmpeg import FFmpegNotFoundError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audio-extractor",
        description="Extract or convert audio from video/audio files using ffmpeg.",
    )
    parser.add_argument("input", type=Path, help="Input video or audio file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <input stem>.<format>)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["wav", "flac", "mp3", "ogg"],
        default="wav",
        help="Output format (default: wav)",
    )
    parser.add_argument(
        "-r",
        "--rate",
        type=int,
        default=16000,
        dest="sample_rate",
        help="Sample rate in Hz (default: 16000)",
    )
    parser.add_argument(
        "--mono",
        action="store_true",
        help="Force mono output (1 channel)",
    )
    parser.add_argument(
        "-c",
        "--channels",
        type=int,
        default=None,
        help="Number of channels (default: 1; overridden by --mono)",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=None,
        help="Start time in seconds",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duration in seconds",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    channels = 1 if args.mono else (args.channels if args.channels is not None else 1)

    try:
        out = extract(
            args.input,
            args.output,
            format=args.format,
            sample_rate=args.sample_rate,
            channels=channels,
            start=args.start,
            duration=args.duration,
        )
    except (FileNotFoundError, ValueError, FFmpegNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
