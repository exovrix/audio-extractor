# audio-extractor

Extract and convert audio tracks from video or audio files using **ffmpeg**.

Supports common containers (`mp4`, `mov`, `webm`, `mkv`, and more) and output formats `wav`, `flac`, `mp3`, and `ogg`.

## Requirements

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/) on your `PATH` (includes `ffprobe`)

Install ffmpeg if needed:

| Platform | Example |
|----------|---------|
| Debian/Ubuntu | `sudo apt install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Windows | `winget install ffmpeg` (or Chocolatey / official builds) |

This library shells out to `ffmpeg`; it does not bundle binaries.

## Install

```bash
pip install git+https://github.com/exovrix/audio-extractor.git
```

Or with Poetry from a local checkout:

```bash
poetry install
```

## CLI

```bash
audio-extractor input.mp4 -o out.wav --rate 16000 --mono
```

Useful options:

```text
audio-extractor INPUT [-o OUTPUT] [-f {wav,flac,mp3,ogg}]
                     [-r RATE] [--mono] [-c CHANNELS]
                     [--start SECONDS] [--duration SECONDS]
```

## Python API

```python
from pathlib import Path
from audio_extractor import extract

out: Path = extract(
    "input.mp4",
    "out.wav",
    format="wav",
    sample_rate=16000,
    channels=1,
)
```

Optional trim:

```python
extract("clip.mkv", format="flac", start=2.5, duration=10.0)
```

## Development

```bash
poetry install
poetry run pytest
```

## Notes

- Requires `ffmpeg` on `PATH` at runtime (Windows WinGet installs work once the install directory is on PATH).
- Default output is 16 kHz mono WAV, a common choice for speech / ASR pipelines.
- Library version: **0.1.0**

## License

MIT

