<div align="center">
  <img src="assets/vstube-icon.png" width="128" alt="Vsy ytd icon">

  # Vsy ytd

  Download videos and extract audio with an elegant, fast, fully local interface.

  <img alt="Windows" src="https://img.shields.io/badge/Windows-10%20%7C%2011-7c4dff?style=for-the-badge&logo=windows11&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-a866ff?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Version" src="https://img.shields.io/badge/version-3.3.0-40e0d0?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-f4f4f5?style=for-the-badge">

  <br><br>
  <a href="https://github.com/frsttw/VStube/releases/latest/download/Vsy-ytd-Setup.exe"><strong>⬇ Download Vsy ytd for Windows</strong></a>
</div>

## About

**Vsy ytd** turns `yt-dlp` and FFmpeg into a focused desktop workflow. Paste a link, choose video or audio, set the quality, and download without opening a terminal.

## Highlights

- Video downloads up to 4K.
- MP3 and M4A audio extraction.
- Support for individual links and playlists.
- Multiple links processed in one batch.
- Automatic memory of the destination folder, format, quality, and preferences.
- Persistent per-folder history to avoid downloading the same video twice.
- Navigation across Downloads, Activity, Preferences, and About.
- Dark interface with violet/cyan accents and readable controls.
- Session log for download and conversion progress.
- Background cancellation, including conversion processes.
- Standalone installer with every required component.

## How to use

1. Download `Vsy-ytd-Setup.exe` from the Releases page.
2. Open Vsy ytd from the Start menu.
3. Paste one or more links, one per line.
4. Choose video or audio and set the quality.
5. Select a destination folder and click **Download now** (or press `Ctrl+Enter`).

The **Preferences** tab can download entire playlists and open the destination when a batch finishes. The **Activity** tab shows the session log. The percentage refers to the current file; video and audio streams may be downloaded separately before they are merged.

> The installer is not digitally signed yet. Windows may show a SmartScreen warning on first launch. The source code is available in this repository for review.

## Included components

| Purpose | Component |
| --- | --- |
| Video and audio extraction | yt-dlp |
| Audio/video merging and conversion | FFmpeg + FFprobe |
| JavaScript runtime for extractors | Deno |
| Desktop interface | Python + Tkinter |
| Windows packaging | PyInstaller + Inno Setup |

The build process updates the bundled `yt-dlp` nightly before creating a new installer so the application can keep up with changes to supported sites.

## Project structure

```text
Vsy ytd/
├── app.py                 # Application state and coordination
├── interface.py           # Navigation, cards, and visual theme
├── engine.py              # Commands, preferences, and download execution
├── test_app.py            # Unit and interface tests
├── test_media.py          # Synthetic local media integration test
├── assets/                # Icon and bundled tools
├── docs/                  # Documentation images
├── VStube.spec            # Executable packaging configuration
├── installer.iss          # Installer configuration
└── build.ps1              # Windows build automation
```

## Build locally

Install Python 3.13, PyInstaller, Inno Setup 6, and the tools listed above. Then run:

```powershell
.\build.ps1
```

The script updates the bundled tools, runs the application tests, creates `dist\Vsy ytd.exe`, and generates `installer\Vsy-ytd-Setup.exe`.

Run the complete test suite with:

```powershell
python -m unittest test_app test_media -v
```

The integration test creates synthetic media with FFmpeg and serves it only on localhost. It does not download YouTube content during validation.

## Privacy and responsible use

Vsy ytd does not run its own server, require an account, or collect telemetry. It connects to the sites represented by the links you provide. Folder, format, quality, and other preferences are stored locally; the activity log stays in the current session.

Use Vsy ytd only for content you own, content in the public domain, or content you are authorized to download. The application does not bypass protections or access private content.

---

<p align="center">Developed by <strong><a href="https://frstt.dev">frstt.dev</a></strong> · <a href="https://github.com/frsttw">@frsttw</a></p>
