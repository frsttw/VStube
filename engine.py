"""Execução dos downloads, independente da interface gráfica."""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "3.2.0"
VIDEO_QUALITIES = ("Melhor disponível", "Até 2160p (4K)", "Até 1440p", "Até 1080p", "Até 720p", "Até 480p", "Até 360p")
AUDIO_FORMATS = ("MP3", "M4A")
DEFAULTS = {"mode": "video", "video_quality": "Até 1080p", "audio_format": "MP3",
            "playlist": False, "open_after": True,
            "output_dir": str(Path.home() / "Downloads" / "Vídeos e áudios")}


def read_settings(path: Path, legacy: Path | None = None) -> dict:
    settings = DEFAULTS.copy()
    try:
        source = legacy if not path.exists() and legacy else path
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return settings
        for key, allowed in (("mode", ("video", "audio")), ("video_quality", VIDEO_QUALITIES), ("audio_format", AUDIO_FORMATS)):
            if data.get(key) in allowed:
                settings[key] = data[key]
        for key in ("playlist", "open_after"):
            if isinstance(data.get(key), bool):
                settings[key] = data[key]
        if isinstance(data.get("output_dir"), str) and data["output_dir"].strip():
            settings["output_dir"] = data["output_dir"]
    except (OSError, ValueError):
        pass
    return settings


def write_settings(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def parse_urls(value: str) -> list[str]:
    urls = list(dict.fromkeys(line.strip() for line in value.splitlines() if line.strip()))
    if not urls:
        raise ValueError("Cole pelo menos um link para começar.")
    for url in urls:
        try:
            parsed = urlsplit(url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname or any(c.isspace() for c in url):
                raise ValueError()
        except ValueError:
            raise ValueError("Use links completos (https://…), um por linha.") from None
    return urls


def build_command(ytdlp: str, ffmpeg: str, urls: list[str], destination: Path, settings: dict) -> list[str]:
    command = [ytdlp, "--ignore-config", "--newline", "--progress", "--no-color", "--encoding", "utf-8",
               "--windows-filenames", "--no-overwrites", "--ffmpeg-location", str(Path(ffmpeg).parent),
               "--yes-playlist" if settings["playlist"] else "--no-playlist"]
    template = "%(title).160B [%(id)s].%(ext)s"
    if settings["playlist"]:
        template = "%(playlist_title|Playlist).100B/%(playlist_index)03d - " + template
    command.extend(["-o", str(destination / template)])
    if settings["mode"] == "audio":
        command.extend(["-x", "--audio-format", settings["audio_format"].lower(), "--audio-quality", "0"])
    else:
        import re
        match = re.search(r"(\d+)p", settings["video_quality"])
        selector = "bv*+ba/b" if not match else f"bv*[height<={match[1]}]+ba/b[height<={match[1]}]"
        command.extend(["-f", selector, "--merge-output-format", "mp4"])
    return command + ["--"] + urls


class DownloadJob:
    def __init__(self, command: list[str], events: queue.Queue):
        self.command, self.events = command, events
        self.cancelled = threading.Event()
        self._lock = threading.Lock()
        self.process = None

    def cancel(self) -> None:
        self.cancelled.set()
        with self._lock:
            process = self.process
            if process is None or process.poll() is not None:
                return
            try:
                if os.name == "nt":
                    taskkill = str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe")
                    result = subprocess.run([taskkill, "/PID", str(process.pid), "/T", "/F"],
                                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                    if result.returncode and process.poll() is None:
                        process.kill()
                else:
                    process.terminate()
            except (OSError, subprocess.TimeoutExpired):
                if process.poll() is None:
                    process.kill()

    def run(self) -> None:
        code, error = 1, ""
        try:
            if self.cancelled.is_set():
                return
            env = os.environ.copy()
            env["PATH"] = str(Path(self.command[0]).parent) + os.pathsep + env.get("PATH", "")
            with self._lock:
                self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            if self.cancelled.is_set():
                self.cancel()
            for line in self.process.stdout:
                line = line.strip()
                self.events.put(("line", line))
                if "ERROR:" in line:
                    error = line.split("ERROR:", 1)[-1].strip()
            code = self.process.wait()
        except Exception as exc:
            error = str(exc)
        finally:
            if self.process and self.process.stdout:
                self.process.stdout.close()
            self.events.put(("finished", (code, error, self.cancelled.is_set())))
