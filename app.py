from __future__ import annotations

import ctypes
import os
import queue
import re
import shutil
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from engine import (DownloadJob, VERSION, read_settings, write_settings, parse_urls,
                    build_command, download_archive_path)
from interface import Interface, PURPLE, BORDER

APP_NAME = "Vsy ytd"
# Keep the configuration location stable across application renames.
SETTINGS_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "VStube"
SETTINGS_FILE = SETTINGS_DIR / "config.json"
LEGACY_SETTINGS_FILE = Path(os.environ.get("APPDATA", str(Path.home()))) / "Baixador de Videos e Audios" / "config.json"


def find_program(name: str) -> str | None:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for folder in (root / "tools", root / "assets" / "tools"):
        candidate = folder / f"{name}.exe"
        if candidate.is_file():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(local.glob(f"**/{name}.exe"))
    return str(matches[0]) if matches else None


class DownloaderApp(Interface, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1080x790")
        self.minsize(940, 700)
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        try:
            self.iconbitmap(str(root / "assets" / "app.ico"))
        except tk.TclError:
            pass
        self.ytdlp, self.ffmpeg = find_program("yt-dlp"), find_program("ffmpeg")
        settings = read_settings(SETTINGS_FILE, LEGACY_SETTINGS_FILE)
        self.mode = tk.StringVar(value=settings["mode"])
        self.video_quality = tk.StringVar(value=settings["video_quality"])
        self.audio_format = tk.StringVar(value=settings["audio_format"])
        self.output_dir = tk.StringVar(value=settings["output_dir"])
        self.playlist = tk.BooleanVar(value=settings["playlist"])
        self.open_after = tk.BooleanVar(value=settings["open_after"])
        self.status = tk.StringVar(value="Pronto para baixar")
        self.progress_text = tk.StringVar(value="")
        self.link_count = tk.StringVar(value="0 links")
        self.busy = False
        self.closing = False
        self.job = None
        self.events = queue.Queue()
        self.save_timer = None
        self.last_destination = None
        self.open_on_finish = False
        self._build_ui()
        self._toggle_mode()
        for var in (self.mode, self.video_quality, self.audio_format, self.output_dir, self.playlist, self.open_after):
            var.trace_add("write", self._schedule_save)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Control-Return>", lambda _e: self.start_download())
        self.after(80, self._drain_events)
        self.after(200, self._check_tools)
        self.after(100, self._dark_titlebar)

    def _dark_titlebar(self):
        if os.name == "nt":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), 4)
            except (AttributeError, OSError):
                pass

    @staticmethod
    def _load_output_dir():
        return read_settings(SETTINGS_FILE, LEGACY_SETTINGS_FILE)["output_dir"]

    def _settings(self):
        return {key: getattr(self, key).get() for key in
                ("mode", "video_quality", "audio_format", "output_dir", "playlist", "open_after")}

    def _schedule_save(self, *_args):
        if self.save_timer:
            self.after_cancel(self.save_timer)
        self.save_timer = self.after(500, self._save_settings)

    def _save_settings(self):
        if self.save_timer:
            self.after_cancel(self.save_timer)
            self.save_timer = None
        data = self._settings()
        if not data["output_dir"].strip():
            data["output_dir"] = self._load_output_dir()
        try:
            write_settings(SETTINGS_FILE, data)
        except OSError as exc:
            self.status.set("Não foi possível salvar as preferências")
            self._append_log(f"Preferências: {exc}")

    def _check_tools(self):
        if not self.ytdlp or not self.ffmpeg:
            self.status.set("Componentes ausentes — reinstale o aplicativo")
            self.download_button.configure(state="disabled")
            self._append_log("Não foi possível localizar yt-dlp ou FFmpeg.")

    def _links_changed(self, _event=None):
        if self.urls.edit_modified():
            count = len({line.strip() for line in self.urls.get("1.0", "end").splitlines() if line.strip()})
            self.link_count.set(f"{count} link" + ("s" if count != 1 else ""))
            self.urls.edit_modified(False)

    def clear_links(self):
        if not self.busy:
            self.urls.delete("1.0", "end")

    def paste(self):
        if self.busy:
            return
        try:
            value = self.clipboard_get().strip()
            if value:
                current = self.urls.get("1.0", "end").strip()
                self.urls.delete("1.0", "end")
                self.urls.insert("1.0", (current + "\n" if current else "") + value)
        except tk.TclError:
            self.status.set("Copie um link antes de colar")

    def choose_output(self):
        selected = filedialog.askdirectory(parent=self, title="Escolha a pasta de destino",
                    initialdir=self.output_dir.get() if Path(self.output_dir.get()).is_dir() else str(Path.home()))
        if selected:
            self.output_dir.set(selected)
            self._save_settings()

    def open_folder(self, destination=None):
        folder = Path(destination or self.output_dir.get().strip())
        try:
            if not folder.is_dir():
                raise OSError("A pasta ainda não existe. Ela será criada ao iniciar o download.")
            os.startfile(folder)
        except OSError as exc:
            messagebox.showinfo(APP_NAME, str(exc), parent=self)

    def _toggle_mode(self):
        for mode, card in self.mode_cards.items():
            card.configure(highlightbackground=PURPLE if mode == self.mode.get() else BORDER)
        self.video_combo.configure(state="readonly" if not self.busy and self.mode.get() == "video" else "disabled")
        self.audio_combo.configure(state="readonly" if not self.busy and self.mode.get() == "audio" else "disabled")

    def _set_busy(self, busy):
        self.busy = busy
        for widget in self.inputs:
            widget.configure(state="disabled" if busy else "normal")
        self.download_button.configure(state="disabled" if busy else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self._toggle_mode()
        if not busy:
            self._check_tools()

    def _command(self, urls, destination):
        settings = self._settings()
        archive = download_archive_path(destination, settings, SETTINGS_DIR / "archives")
        archive.parent.mkdir(parents=True, exist_ok=True)
        return build_command(self.ytdlp, self.ffmpeg, urls, destination, settings, archive)

    def start_download(self):
        if self.busy:
            return
        if not self.ytdlp or not self.ffmpeg:
            self._check_tools()
            return
        try:
            urls = parse_urls(self.urls.get("1.0", "end"))
            if not self.output_dir.get().strip():
                raise ValueError("Escolha uma pasta de destino.")
            destination = Path(self.output_dir.get().strip()).expanduser().resolve()
            destination.mkdir(parents=True, exist_ok=True)
        except (ValueError, OSError) as exc:
            messagebox.showwarning(APP_NAME, str(exc), parent=self)
            return
        self._save_settings()
        self.last_destination = destination
        self.open_on_finish = self.open_after.get()
        self._set_busy(True)
        self.status.set("Preparando o download…")
        self.progress_text.set("Conectando")
        self.progress.configure(mode="indeterminate", value=0)
        self.progress.start(15)
        self._append_log(f"\nNovo lote: {len(urls)} link(s) · {self.mode.get()} · {destination}")
        self.job = DownloadJob(self._command(urls, destination), self.events)
        threading.Thread(target=self.job.run, daemon=True).start()

    def _append_log(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        count = int(self.log.index("end-1c").split(".")[0])
        if count > 400:
            self.log.delete("1.0", f"{count - 399}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _drain_events(self):
        for _ in range(150):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "finished":
                self._finished(*value)
                if self.closing:
                    return
            else:
                self._append_log(value)
                if self.job and self.job.cancelled.is_set():
                    continue
                match = re.search(r"\[download\]\s+([\d.]+)%", value)
                if match:
                    percent = min(100, float(match[1]))
                    self.progress.stop()
                    self.progress.configure(mode="determinate", value=percent)
                    self.progress_text.set(value.replace("[download]", "").strip())
                    self.status.set("Baixando · progresso do arquivo atual")
                elif "[Merger]" in value or "[ExtractAudio]" in value:
                    self.progress.configure(mode="indeterminate")
                    self.progress.start(15)
                    self.status.set("Finalizando o arquivo…")
                    self.progress_text.set("Conversão")
        self.after(80, self._drain_events)

    def cancel(self):
        if self.busy and self.job:
            self.status.set("Cancelando download e conversão…")
            self.cancel_button.configure(state="disabled")
            # Cancellation is also asynchronous; Windows may take a moment to stop the process tree.
            self.job.cancelled.set()
            threading.Thread(target=self.job.cancel, daemon=True).start()

    def _finished(self, code, error, cancelled):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self._set_busy(False)
        self.progress_text.set("")
        if cancelled:
            self.status.set("Download cancelado")
            self._append_log("Cancelado. Arquivos parciais são mantidos para permitir retomada.")
        elif code == 0:
            self.progress.configure(value=100)
            self.status.set("Concluído · arquivos disponíveis na pasta")
            if self.open_on_finish and not self.closing:
                self.open_folder(self.last_destination)
        else:
            self.status.set("Não foi possível concluir · confira Atividade")
            self._append_log(error or "O processo terminou com erro.")
            self.show_page("activity")
            if not self.closing:
                messagebox.showerror(APP_NAME, "O download não foi concluído.\n\n" +
                    (error or "Confira o registro na aba Atividade."), parent=self)
        self.job = None
        if self.closing:
            self.destroy()

    def close(self):
        if self.busy:
            if not messagebox.askyesno(APP_NAME, "Cancelar o download em andamento e fechar?", parent=self):
                return
            self.closing = True
            self.cancel()
        self._save_settings()
        if not self.busy:
            self.destroy()

    def destroy(self):
        for timer in self.tk.splitlist(self.tk.call("after", "info")):
            self.after_cancel(timer)
        super().destroy()


if __name__ == "__main__":
    DownloaderApp().mainloop()
