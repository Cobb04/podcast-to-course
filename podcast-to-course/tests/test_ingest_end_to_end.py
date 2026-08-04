import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from ingest_podcast import main  # noqa: E402


class _AudioHandler(BaseHTTPRequestHandler):
    payload = b"fake-m4a-audio"

    def _headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "audio/mp4")
        self.send_header("Content-Length", str(len(self.payload)))
        self.end_headers()

    def do_HEAD(self):  # noqa: N802
        self._headers()

    def do_GET(self):  # noqa: N802
        self._headers()
        self.wfile.write(self.payload)

    def log_message(self, *args):
        return


class IngestEndToEndTests(unittest.TestCase):
    def test_audio_url_to_transcript_with_local_provider(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _AudioHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                fake_cli = tmp_path / "fake-whisperkit"
                fake_cli.write_text(
                    """#!/usr/bin/env python3
import json
import pathlib
import sys
args = sys.argv[1:]
audio = pathlib.Path(args[args.index('--audio-path') + 1])
report_dir = pathlib.Path(args[args.index('--report-path') + 1])
report_dir.mkdir(parents=True, exist_ok=True)
native = {
    'text': 'hello world',
    'language': 'en',
    'segments': [{'start': 0.0, 'end': 1.0, 'text': 'hello world'}],
}
(report_dir / (audio.stem + '.json')).write_text(json.dumps(native))
(report_dir / (audio.stem + '.srt')).write_text('hello world')
print('SPEAKER episode 1 0.000 1.000 hello world <NA> A <NA> <NA>')
""",
                    encoding="utf-8",
                )
                os.chmod(fake_cli, 0o755)
                out_dir = tmp_path / "output"
                url = f"http://127.0.0.1:{server.server_port}/episode.m4a"

                exit_code = main(
                    [
                        "--audio-url",
                        url,
                        "--provider",
                        "whisperkit",
                        "--whisperkit-cli",
                        str(fake_cli),
                        "--language",
                        "en",
                        "--out",
                        str(out_dir),
                    ]
                )

                transcript = (out_dir / "transcript.md").read_text(encoding="utf-8")
                report = (out_dir / "ingest_report.md").read_text(encoding="utf-8")
                raw = json.loads(
                    (out_dir / "raw_transcription.json").read_text(encoding="utf-8")
                )
                self.assertEqual(exit_code, 0)
                self.assertIn("Transcribed by: WhisperKit (local)", transcript)
                self.assertIn("Speaker A: hello world", transcript)
                self.assertIn("Selected provider: whisperkit", report)
                self.assertEqual(raw["Provider"], "whisperkit")
                self.assertTrue((out_dir / "source_audio.m4a").exists())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
