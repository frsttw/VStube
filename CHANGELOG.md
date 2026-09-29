# Changelog

All notable Vsy ytd changes are documented in this file.

## [3.3.0] - 2026-08-29

- Added persistent `yt-dlp` history to ignore repeated videos on pages with duplicate items.
- History is separated by destination folder, mode, and quality so intentional downloads remain available.

## [3.2.0] - 2026-08-27

- Updated the bundled `yt-dlp` to follow recent YouTube changes and fix HTTP 403 download failures.
- The build process now updates the component automatically before creating an installer.

## [3.1.0] - 2026-08-26

- Added a subtle `frstt.dev` signature to the application footer.
- Added a clickable credit to the About page and README.

## [3.0.0] - 2026-08-26

- New navigation layout with video/audio cards and a violet/cyan palette.
- Activity, Preferences, and About tabs with working actions.
- Atomic preference storage, including format and quality.
- Event queue execution to keep the interface responsive during downloads.
- Download and conversion cancellation, with confirmation when closing an active task.
- Link deduplication and destination-folder error handling.
- Automated tests and video/MP3 integration using synthetic local media.

## [2.1.0] - 2026-08-26

- Renamed the application to Vsy ytd while preserving previous preferences.
- Updated the executable, installer, and shortcuts with the new name.

## [2.0.0] - 2026-08-26

- Real transparency in the icon corners.
- Removed the residual dark border around the edges.
- Improved icon rendering on GitHub and at small Windows sizes.

## [1.0.0] - 2026-08-26

- Dark interface with violet and cyan accents.
- Standalone installer for Windows 10 and 11.
- Automatic memory of the last destination folder.
- Video downloads at multiple resolutions.
- MP3 and M4A audio extraction.
- Playlist and multiple-link support.
