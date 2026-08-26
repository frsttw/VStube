"""Teste de integração sem acesso à internet: mídia sintética servida em localhost."""
import functools
import http.server
import queue
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from app import find_program
from engine import DEFAULTS, DownloadJob, build_command


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class MediaIntegrationTests(unittest.TestCase):
    def test_video_and_mp3(self):
        ffmpeg, ytdlp = find_program('ffmpeg'), find_program('yt-dlp')
        if not ffmpeg or not ytdlp:
            self.skipTest('FFmpeg e yt-dlp necessários para integração')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.mp4'
            result = subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
                'color=c=purple:s=320x240:r=25', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=44100',
                '-t', '2', '-c:v', 'mpeg4', '-c:a', 'aac', str(source)], capture_output=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode, 0, result.stderr)
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=directory))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_port}/source.mp4'
                for mode, extension in (('video', 'mp4'), ('audio', 'mp3')):
                    dest = root / mode
                    dest.mkdir()
                    settings = dict(DEFAULTS, mode=mode, video_quality='Melhor disponível')
                    events = queue.Queue()
                    job = DownloadJob(build_command(ytdlp, ffmpeg, [url], dest, settings), events)
                    worker = threading.Thread(target=job.run, daemon=True)
                    worker.start()
                    worker.join(timeout=45)
                    if worker.is_alive():
                        job.cancel()
                        worker.join(timeout=10)
                        self.fail('Tempo limite de integração excedido')
                    records = []
                    while not events.empty():
                        records.append(events.get())
                    self.assertEqual(records[-1][0], 'finished')
                    self.assertEqual(records[-1][1][0], 0, records)
                    files = list(dest.glob(f'*.{extension}'))
                    self.assertEqual(len(files), 1)
                    self.assertGreater(files[0].stat().st_size, 1000)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main()
