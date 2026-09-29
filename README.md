<p align="center"><img src="assets/vstube-icon.png" width="128" alt="Vsy ytd icon"></p>

<h1 align="center">Vsy ytd</h1>

<p align="center">A local desktop interface for downloading videos and extracting audio.</p>

## Overview

Vsy ytd provides a visual Windows interface for the existing **yt-dlp** and **FFmpeg** command-line tools. It coordinates links, quality settings, output folders, progress, cancellation, and media conversion without requiring the user to open a terminal. The application does not implement a media downloader from scratch; it orchestrates these established tools through a desktop workflow.

## Features

- Video downloads up to 4K, depending on the source.
- Audio extraction to MP3 or M4A through FFmpeg.
- Individual links and playlists.
- Multiple links processed in one session.
- Progress reporting and cancellation.
- Remembered folders, formats, quality, and preferences.
- Session history and duplicate-download protection.
- Dark interface for Windows 10 and 11.
- Standalone installer with the required components.

## Technology stack

| Layer | Technology |
| --- | --- |
| Interface | Python + Tkinter/ttk |
| Download engine | yt-dlp |
| Audio and video processing | FFmpeg + FFprobe |
| Auxiliary runtime | Deno |
| Packaging | PyInstaller |
| Installer | Inno Setup |

## Usage

1. Download the latest installer from [Releases](https://github.com/frsttw/VStube/releases).
2. Install and open Vsy ytd.
3. Paste one or more links.
4. Select video or audio and choose the quality.
5. Select a destination folder and start the download.

## Build and tests

Install Python, PyInstaller, Inno Setup, yt-dlp, FFmpeg, and Deno, then run:

```powershell
.\build.ps1
python -m unittest test_app test_media -v
```

The integration tests generate synthetic local media with FFmpeg and do not download content from external services.

## Responsible use

Use Vsy ytd only for content you own, content in the public domain, or content you are authorized to download. The application does not bypass protections or access private content.

## License

MIT License. See [LICENSE](LICENSE).

<p align="center">Built by <a href="https://frstt.dev">frstt.dev</a> · <a href="https://github.com/frsttw">@frsttw</a></p>
