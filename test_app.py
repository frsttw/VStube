import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from engine import (DEFAULTS, DownloadJob, build_command, download_archive_path,
                    parse_urls, read_settings, write_settings)


class SettingsTests(unittest.TestCase):
    def test_atomic_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            expected = dict(DEFAULTS, output_dir='D:/Vídeos', mode='audio', open_after=False)
            write_settings(path, expected)
            self.assertEqual(read_settings(path), expected)
            self.assertFalse(path.with_suffix('.tmp').exists())

    def test_invalid_and_legacy_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            path, legacy = Path(directory) / 'new.json', Path(directory) / 'old.json'
            write_settings(legacy, dict(DEFAULTS, output_dir='D:/antiga'))
            self.assertEqual(read_settings(path, legacy)['output_dir'], 'D:/antiga')
            for data in ('[]', '{', 'null', '{"mode":"bad", "playlist":"yes"}'):
                path.write_text(data, encoding='utf-8')
                self.assertEqual(read_settings(path, legacy), DEFAULTS)


class CommandTests(unittest.TestCase):
    def test_urls(self):
        self.assertEqual(parse_urls('https://youtu.be/a\nhttps://youtu.be/a\n'), ['https://youtu.be/a'])
        for value in ('', '--exec something', 'https://', 'https://abc /x', 'file:///c:/a'):
            with self.assertRaises(ValueError):
                parse_urls(value)

    def test_modes(self):
        for mode in ('video', 'audio'):
            for playlist in (True, False):
                settings = dict(DEFAULTS, mode=mode, playlist=playlist)
                command = build_command('yt-dlp.exe', 'C:/tools/ffmpeg.exe', ['https://youtu.be/a'], Path('C:/Videos'), settings)
                self.assertIn('--yes-playlist' if playlist else '--no-playlist', command)
                self.assertIn('-x' if mode == 'audio' else '-f', command)
                self.assertEqual(command[-2:], ['--', 'https://youtu.be/a'])
                self.assertIn('--no-overwrites', command)

    def test_archive_option_and_variants(self):
        with tempfile.TemporaryDirectory() as directory:
            destination, archive_root = Path(directory) / 'Videos', Path(directory) / 'archives'
            video = download_archive_path(destination, dict(DEFAULTS, mode='video'), archive_root)
            audio = download_archive_path(destination, dict(DEFAULTS, mode='audio'), archive_root)
            self.assertEqual(video, download_archive_path(destination, dict(DEFAULTS, mode='video'), archive_root))
            self.assertNotEqual(video, audio)
            command = build_command('yt-dlp.exe', 'C:/tools/ffmpeg.exe', ['https://youtu.be/a'],
                                    destination, dict(DEFAULTS), video)
            self.assertEqual(command[-4:-2], ['--download-archive', str(video)])


class WorkerTests(unittest.TestCase):
    def run_job(self, script):
        events = queue.Queue()
        job = DownloadJob([sys.executable, '-u', '-c', script], events)
        job.run()
        result = []
        while not events.empty():
            result.append(events.get())
        return result

    def test_success_and_failure(self):
        result = self.run_job("print('[download] 50%'); print('done')")
        self.assertEqual(result[-1], ('finished', (0, '', False)))
        result = self.run_job("import sys; print('ERROR: teste'); sys.exit(1)")
        self.assertEqual(result[-1], ('finished', (1, 'teste', False)))

    def test_cancel_before_spawn(self):
        events = queue.Queue()
        job = DownloadJob(['not-a-program'], events)
        job.cancel()
        job.run()
        self.assertTrue(events.get()[1][2])

    def test_cancel_running_tree(self):
        events = queue.Queue()
        # A descendant keeps stdout open unless the whole tree is stopped.
        script = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); print('ready',flush=True); time.sleep(30)"
        job = DownloadJob([sys.executable, '-u', '-c', script], events)
        thread = threading.Thread(target=job.run, daemon=True)
        thread.start()
        self.assertEqual(events.get(timeout=10), ('line', 'ready'))
        job.cancel()
        thread.join(timeout=10)
        self.assertFalse(thread.is_alive())
        self.assertTrue(events.get(timeout=3)[1][2])


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = patch.object(app, 'SETTINGS_FILE', Path(self.temp.name) / 'config.json')
        self.settings.start()
        self.ui = app.DownloaderApp()
        self.ui.withdraw()
        self.ui.update()

    def tearDown(self):
        self.ui.destroy()
        self.settings.stop()
        self.temp.cleanup()

    def test_navigation_modes_and_busy_state(self):
        for page in ('downloads', 'settings', 'activity', 'about'):
            self.ui.show_page(page)
            self.assertEqual(self.ui.current_page, page)
        self.ui.mode.set('audio')
        self.ui._toggle_mode()
        self.assertEqual(str(self.ui.audio_combo.cget('state')), 'readonly')
        self.ui._set_busy(True)
        self.assertEqual(str(self.ui.audio_combo.cget('state')), 'disabled')
        self.ui._set_busy(False)
        self.assertEqual(str(self.ui.audio_combo.cget('state')), 'readonly')

    def test_site_credit(self):
        self.assertEqual(self.ui.site_mark.cget('text'), 'frstt.dev')
        self.assertEqual(self.ui.site_mark.cget('cursor'), 'hand2')

    def test_preferences_and_log_limit(self):
        self.ui.output_dir.set('D:/Músicas')
        self.ui.open_after.set(False)
        self.ui._save_settings()
        self.assertEqual(read_settings(app.SETTINGS_FILE)['output_dir'], 'D:/Músicas')
        for _ in range(410):
            self.ui._append_log('test')
        self.assertLessEqual(int(self.ui.log.index('end-1c').split('.')[0]), 400)

    def test_minimum_layout_keeps_controls_visible(self):
        self.ui.geometry('940x700')
        self.ui.deiconify()
        self.ui.update()
        for page in ('downloads', 'activity', 'settings', 'about'):
            self.ui.show_page(page)
            self.ui.update()
            self.assertGreaterEqual(self.ui.download_button.winfo_height(), self.ui.download_button.winfo_reqheight())
        self.ui.show_page('downloads')
        self.ui.update()
        for widget in (self.ui.video_combo, self.ui.audio_combo, self.ui.inputs[2]):
            self.assertGreaterEqual(widget.winfo_height(), widget.winfo_reqheight())

    def test_worker_events_finish_without_tk_calls_from_thread(self):
        self.ui.open_on_finish = False
        self.ui._set_busy(True)
        self.ui.events.put(('line', '[download] 42.5% of 1MiB at 1MiB/s ETA 00:00'))
        self.ui.events.put(('finished', (0, '', False)))
        self.ui._drain_events()
        self.assertFalse(self.ui.busy)
        self.assertEqual(self.ui.progress['value'], 100)

    def test_duplicate_launch_and_bad_destination(self):
        self.ui.busy = True
        with patch.object(app, 'DownloadJob') as job:
            self.ui.start_download()
            job.assert_not_called()
        self.ui.busy = False
        self.ui.urls.insert('1.0', 'https://youtu.be/example')
        self.ui.output_dir.set('')
        with patch.object(app.messagebox, 'showwarning') as warning:
            self.ui.start_download()
            warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
