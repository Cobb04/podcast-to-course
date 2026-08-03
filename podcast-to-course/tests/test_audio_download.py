import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audio_download import download_public_audio, infer_audio_suffix  # noqa: E402


class _AudioHandler(BaseHTTPRequestHandler):
    payload = b"ID3-podcast-audio"
    ranges = []

    def do_GET(self):  # noqa: N802
        range_header = self.headers.get("Range")
        self.__class__.ranges.append(range_header)
        start = int(range_header.removeprefix("bytes=").removesuffix("-")) if range_header else 0
        body = self.payload[start:]
        self.send_response(206 if range_header else 200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


class AudioDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _AudioHandler.ranges = []
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _AudioHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_infers_suffix_from_url_then_content_type(self):
        self.assertEqual(infer_audio_suffix("https://example.com/a.m4a?x=1"), ".m4a")
        self.assertEqual(infer_audio_suffix("https://example.com/media", "audio/mpeg"), ".mp3")

    def test_downloads_public_audio_to_stable_cache_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = download_public_audio(
                f"{self.base_url}/episode.mp3", Path(tmp), chunk_size=4
            )

            self.assertEqual(path.name, "source_audio.mp3")
            self.assertEqual(path.read_bytes(), _AudioHandler.payload)

    def test_resumes_partial_download_with_range_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            partial = Path(tmp) / "source_audio.mp3.part"
            partial.write_bytes(_AudioHandler.payload[:3])

            path = download_public_audio(f"{self.base_url}/episode.mp3", Path(tmp))

            self.assertEqual(path.read_bytes(), _AudioHandler.payload)
            self.assertEqual(_AudioHandler.ranges[-1], "bytes=3-")


if __name__ == "__main__":
    unittest.main()
