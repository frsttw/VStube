from __future__ import annotations

import os
import json
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_NAME = "Baixador de Vídeos e Áudios"
SETTINGS_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "Baixador de Videos e Audios"
SETTINGS_FILE = SETTINGS_DIR / "config.json"
VIDEO_QUALITIES = ("Melhor disponível", "Até 2160p (4K)", "Até 1440p", "Até 1080p", "Até 720p", "Até 480p", "Até 360p")
AUDIO_FORMATS = ("MP3", "M4A")


def find_program(name: str) -> str | None:
    bundled_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    bundled = bundled_root / "tools" / f"{name}.exe"
    if bundled.exists():
        return str(bundled)
    found = shutil.which(name)
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = list((local / "Microsoft" / "WinGet" / "Packages").glob(f"**/{name}.exe"))
    candidates += list((local / "Microsoft" / "WindowsApps").glob(f"{name}.exe"))
    return str(sorted(candidates, key=lambda p: len(str(p)))[0]) if candidates else None


class DownloaderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("830x650")
        self.minsize(720, 590)
        self.ytdlp = find_program("yt-dlp")
        self.ffmpeg = find_program("ffmpeg")
        self.process: subprocess.Popen[str] | None = None

        self.mode = tk.StringVar(value="video")
        self.video_quality = tk.StringVar(value="Até 1080p")
        self.audio_format = tk.StringVar(value="MP3")
        self.output_dir = tk.StringVar(value=self._load_output_dir())
        self.playlist = tk.BooleanVar(value=False)
        self.open_after = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Pronto para baixar.")
        self.progress_text = tk.StringVar(value="")
        self._build_ui()
        self.after(200, self._check_tools)

    @staticmethod
    def _load_output_dir() -> str:
        default = str(Path.home() / "Downloads" / "Vídeos e áudios")
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            saved = data.get("output_dir")
            return saved if isinstance(saved, str) and saved.strip() else default
        except (OSError, ValueError, TypeError):
            return default

    @staticmethod
    def _save_output_dir(directory: str) -> None:
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(json.dumps({"output_dir": directory}, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _build_ui(self) -> None:
        self.configure(bg="#f4f6f8")
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"), background="#f4f6f8")
        style.configure("Hint.TLabel", font=("Segoe UI", 10), foreground="#52606d", background="#f4f6f8")
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=(18, 10))

        root = ttk.Frame(self, padding=22)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Baixador de Vídeos e Áudios", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Baixe conteúdo que você tem permissão para salvar, sem usar o terminal.", style="Hint.TLabel").pack(anchor="w", pady=(2, 16))

        link_box = ttk.LabelFrame(root, text="1. Link do YouTube", padding=10)
        link_box.pack(fill="both", expand=True)
        ttk.Label(link_box, text="Cole um ou mais links (um por linha):").pack(anchor="w", pady=(0, 6))
        text_frame = ttk.Frame(link_box)
        text_frame.pack(fill="both", expand=True)
        self.urls = tk.Text(text_frame, height=7, wrap="word", font=("Segoe UI", 10), undo=True, borderwidth=1, relief="solid")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.urls.yview)
        self.urls.configure(yscrollcommand=scrollbar.set)
        self.urls.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        buttons = ttk.Frame(link_box)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Colar", command=self.paste).pack(side="left")
        ttk.Button(buttons, text="Limpar", command=lambda: self.urls.delete("1.0", "end")).pack(side="left", padx=8)

        format_box = ttk.LabelFrame(root, text="2. Formato", padding=10)
        format_box.pack(fill="x", pady=12)
        ttk.Radiobutton(format_box, text="Vídeo", variable=self.mode, value="video", command=self._toggle_mode).grid(row=0, column=0, sticky="w")
        self.video_combo = ttk.Combobox(format_box, textvariable=self.video_quality, values=VIDEO_QUALITIES, state="readonly", width=22)
        self.video_combo.grid(row=0, column=1, sticky="w", padx=(8, 28))
        ttk.Radiobutton(format_box, text="Somente áudio", variable=self.mode, value="audio", command=self._toggle_mode).grid(row=0, column=2, sticky="w")
        self.audio_combo = ttk.Combobox(format_box, textvariable=self.audio_format, values=AUDIO_FORMATS, state="disabled", width=8)
        self.audio_combo.grid(row=0, column=3, sticky="w", padx=8)
        ttk.Checkbutton(format_box, text="Baixar playlist inteira", variable=self.playlist).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Checkbutton(format_box, text="Abrir pasta ao concluir", variable=self.open_after).grid(row=1, column=2, columnspan=2, sticky="w", pady=(12, 0))

        destination = ttk.LabelFrame(root, text="3. Onde salvar", padding=10)
        destination.pack(fill="x")
        ttk.Entry(destination, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(destination, text="Escolher pasta...", command=self.choose_output).pack(side="left", padx=(8, 0))

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(14, 0))
        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        status_line = ttk.Frame(bottom)
        status_line.pack(fill="x", pady=(7, 0))
        ttk.Label(status_line, textvariable=self.status).pack(side="left")
        ttk.Label(status_line, textvariable=self.progress_text).pack(side="left", padx=10)
        self.cancel_button = ttk.Button(status_line, text="Cancelar", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="right", padx=(8, 0))
        self.download_button = ttk.Button(status_line, text="Baixar agora", style="Accent.TButton", command=self.start_download)
        self.download_button.pack(side="right")

    def _check_tools(self) -> None:
        missing = []
        if not self.ytdlp:
            missing.append("yt-dlp")
        if not self.ffmpeg:
            missing.append("FFmpeg")
        if missing:
            messagebox.showerror(APP_NAME, "Não foi possível localizar: " + ", ".join(missing) + ".\n\nReinstale o aplicativo ou esses componentes.")

    def paste(self) -> None:
        try:
            value = self.clipboard_get().strip()
            if value:
                if self.urls.get("1.0", "end").strip():
                    self.urls.insert("end", "\n")
                self.urls.insert("end", value)
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "A área de transferência não contém texto.")

    def choose_output(self) -> None:
        selected = filedialog.askdirectory(title="Escolha a pasta de destino", initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)
            self._save_output_dir(selected)

    def _toggle_mode(self) -> None:
        is_video = self.mode.get() == "video"
        self.video_combo.configure(state="readonly" if is_video else "disabled")
        self.audio_combo.configure(state="disabled" if is_video else "readonly")

    def _video_height(self) -> str | None:
        match = re.search(r"(\d+)p", self.video_quality.get())
        return match.group(1) if match else None

    def _command(self, urls: list[str], destination: Path) -> list[str]:
        command = [self.ytdlp or "yt-dlp", "--newline", "--progress", "--windows-filenames", "--ffmpeg-location", str(Path(self.ffmpeg or "ffmpeg").parent)]
        command.append("--yes-playlist" if self.playlist.get() else "--no-playlist")
        template = "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s" if self.playlist.get() else "%(title)s.%(ext)s"
        command.extend(["-o", str(destination / template)])
        if self.mode.get() == "audio":
            audio = self.audio_format.get().lower()
            command.extend(["-x", "--audio-format", audio, "--audio-quality", "0"])
        else:
            height = self._video_height()
            selector = "bv*+ba/b" if not height else f"bv*[height<={height}]+ba/b[height<={height}]"
            command.extend(["-f", selector, "--merge-output-format", "mp4"])
        command.extend(urls)
        return command

    def start_download(self) -> None:
        if not self.ytdlp or not self.ffmpeg:
            self._check_tools()
            return
        urls = [line.strip() for line in self.urls.get("1.0", "end").splitlines() if line.strip()]
        if not urls:
            messagebox.showinfo(APP_NAME, "Cole pelo menos um link do YouTube.")
            return
        if any(not re.match(r"^https?://", url, re.I) for url in urls):
            messagebox.showwarning(APP_NAME, "Cada linha precisa conter um link completo começando com http:// ou https://.")
            return
        destination = Path(self.output_dir.get().strip())
        if not self.output_dir.get().strip():
            messagebox.showwarning(APP_NAME, "Escolha uma pasta de destino.")
            return
        destination.mkdir(parents=True, exist_ok=True)
        self._save_output_dir(str(destination))
        self.download_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.configure(value=0)
        self.progress_text.set("")
        self.status.set("Preparando o download...")
        command = self._command(urls, destination)
        threading.Thread(target=self._run_download, args=(command, destination), daemon=True).start()

    def _run_download(self, command: list[str], destination: Path) -> None:
        try:
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process_env = os.environ.copy()
            tools_dir = str(Path(self.ytdlp or "").parent)
            process_env["PATH"] = tools_dir + os.pathsep + process_env.get("PATH", "")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW, env=process_env)
            self.process = process
            assert process.stdout
            last_error = ""
            for line in process.stdout:
                line = line.strip()
                match = re.search(r"\[download\]\s+([\d.]+)%", line)
                if match:
                    value = float(match.group(1))
                    self.after(0, self.progress.configure, {"value": value})
                    self.after(0, self.progress_text.set, f"{value:.1f}%")
                    self.after(0, self.status.set, "Baixando...")
                elif "[Merger]" in line or "[ExtractAudio]" in line:
                    self.after(0, self.status.set, "Finalizando o arquivo...")
                elif "ERROR:" in line:
                    last_error = line.split("ERROR:", 1)[-1].strip()
            code = process.wait()
            cancelled = code != 0 and self.process is None
            self.after(0, self._finished, destination, code, last_error, cancelled)
        except Exception as exc:
            self.after(0, self._finished, destination, 1, str(exc), False)

    def cancel(self) -> None:
        if self.process and self.process.poll() is None:
            process = self.process
            self.process = None
            process.terminate()
            self.status.set("Cancelando...")

    def _finished(self, destination: Path, code: int, error: str, cancelled: bool) -> None:
        self.process = None
        self.download_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        if cancelled:
            self.status.set("Download cancelado.")
            return
        if code == 0:
            self.progress.configure(value=100)
            self.progress_text.set("100%")
            self.status.set("Concluído com sucesso!")
            if self.open_after.get():
                os.startfile(destination)
        else:
            self.status.set("Não foi possível concluir o download.")
            messagebox.showerror(APP_NAME, "O download falhou.\n\n" + (error or "Verifique o link e sua conexão com a internet."))


if __name__ == "__main__":
    DownloaderApp().mainloop()
