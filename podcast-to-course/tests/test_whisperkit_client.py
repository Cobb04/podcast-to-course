import json
import inspect
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from whisperkit_client import (  # noqa: E402
    WhisperKitError,
    build_whisperkit_command,
    canonicalize_whisperkit_result,
    parse_rttm_output,
    transcribe_with_whisperkit,
    write_canonical_transcription,
)
from normalize_transcript import normalize_to_markdown  # noqa: E402


class WhisperKitCommandTests(unittest.TestCase):
    def test_builds_long_audio_command_with_reports_and_diarization(self):
        command = build_whisperkit_command(
            "whisperkit-cli",
            Path("/tmp/episode.m4a"),
            Path("/tmp/reports"),
            model="large-v3-v20240930_626MB",
            language="zh",
            diarization=True,
            speaker_count=2,
        )

        self.assertEqual(command[:2], ["whisperkit-cli", "transcribe"])
        self.assertIn("--incremental-loading", command)
        self.assertEqual(command[command.index("--chunking-strategy") + 1], "vad")
        self.assertEqual(command[command.index("--audio-path") + 1], "/tmp/episode.m4a")
        self.assertEqual(command[command.index("--model") + 1], "large-v3-v20240930_626MB")
        self.assertEqual(command[command.index("--language") + 1], "zh")
        self.assertIn("--word-timestamps", command)
        self.assertIn("--report", command)
        self.assertEqual(command[command.index("--report-path") + 1], "/tmp/reports")
        self.assertIn("--diarization", command)
        self.assertEqual(command[command.index("--diarization-num-speakers") + 1], "2")

    def test_uses_local_model_path_without_requesting_remote_model(self):
        self.assertIn(
            "model_path", inspect.signature(build_whisperkit_command).parameters
        )
        command = build_whisperkit_command(
            "argmax-cli",
            Path("/tmp/episode.m4a"),
            Path("/tmp/reports"),
            model="remote-model",
            model_path=Path("/models/whisper-large-v3"),
        )

        self.assertEqual(
            command[command.index("--model-path") + 1],
            "/models/whisper-large-v3",
        )
        self.assertNotIn("--model", command)

    def test_uses_local_diarization_model_path(self):
        self.assertIn(
            "diarization_model_path",
            inspect.signature(build_whisperkit_command).parameters,
        )
        command = build_whisperkit_command(
            "argmax-cli",
            Path("/tmp/episode.m4a"),
            Path("/tmp/reports"),
            diarization=True,
            diarization_model_path=Path("/models/speakerkit"),
        )

        self.assertEqual(
            command[command.index("--diarization-model-path") + 1],
            "/models/speakerkit",
        )


class WhisperKitResultTests(unittest.TestCase):
    def test_parses_rttm_with_multiword_orthography(self):
        stdout = """
transcript text
---- Speaker Diarization Results ----
SPEAKER episode 1 0.500 2.250 你好 世界 <NA> A <NA> <NA>
SPEAKER episode 1 2.750 1.000 再见 <NA> B <NA> <NA>
"""

        self.assertEqual(
            parse_rttm_output(stdout),
            [
                {"start": 0.5, "end": 2.75, "text": "你好世界", "speaker": "A"},
                {"start": 2.75, "end": 3.75, "text": "再见", "speaker": "B"},
            ],
        )

    def test_rttm_removes_cjk_token_spaces_but_keeps_english_word_spaces(self):
        stdout = (
            "SPEAKER episode 1 0.000 2.000 跟 这些 人 say hello 和 say goodbye "
            "<NA> A <NA> <NA>"
        )

        segment = parse_rttm_output(stdout)[0]

        self.assertEqual(segment["text"], "跟这些人say hello和say goodbye")

    def test_rttm_repairs_negative_durations_and_sorts_out_of_order_turns(self):
        stdout = """\
SPEAKER episode 1 10.000 0.500 first <NA> A <NA> <NA>
SPEAKER episode 1 15.000 -4.000 repaired <NA> B <NA> <NA>
SPEAKER episode 1 11.500 1.000 third <NA> A <NA> <NA>
"""

        self.assertEqual(
            parse_rttm_output(stdout),
            [
                {"start": 10.0, "end": 10.5, "text": "first", "speaker": "A"},
                {
                    "start": 10.5,
                    "end": 11.0,
                    "text": "repaired",
                    "speaker": "B",
                },
                {"start": 11.5, "end": 12.5, "text": "third", "speaker": "A"},
            ],
        )

    def test_prefers_diarization_segments_for_canonical_output(self):
        native = {
            "text": "你好世界再见",
            "language": "zh",
            "segments": [{"start": 0.0, "end": 4.0, "text": "你好世界再见"}],
        }
        rttm = [
            {"start": 0.5, "end": 2.75, "text": "你好世界", "speaker": "A"},
            {"start": 2.75, "end": 3.75, "text": "再见", "speaker": "B"},
        ]

        canonical = canonicalize_whisperkit_result(native, rttm)

        self.assertEqual(canonical["Provider"], "whisperkit")
        transcription = canonical["Transcription"]
        self.assertEqual(transcription["AudioInfo"]["Duration"], 4000)
        self.assertEqual(transcription["AudioInfo"]["Language"], "zh")
        self.assertEqual(transcription["Paragraphs"][0]["SpeakerId"], "A")
        self.assertEqual(
            transcription["Paragraphs"][0]["Words"],
            [{"Start": 500, "End": 2750, "Text": "你好世界"}],
        )

    def test_falls_back_to_native_segments_without_diarization(self):
        native = {
            "text": "Hello world",
            "language": "en",
            "segments": [
                {
                    "start": 0.25,
                    "end": 1.5,
                    "text": "Hello world",
                    "words": [
                        {"word": "Hello", "start": 0.25, "end": 0.8},
                        {"word": " world", "start": 0.8, "end": 1.5},
                    ],
                }
            ],
        }

        canonical = canonicalize_whisperkit_result(native, [])
        paragraph = canonical["Transcription"]["Paragraphs"][0]

        self.assertNotIn("SpeakerId", paragraph)
        self.assertEqual(
            paragraph["Words"],
            [
                {"Start": 250, "End": 800, "Text": "Hello"},
                {"Start": 800, "End": 1500, "Text": " world"},
            ],
        )

    def test_writes_canonical_json(self):
        native = {
            "text": "test",
            "language": "en",
            "segments": [{"start": 0.0, "end": 1.0, "text": "test"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "raw_transcription.json"
            write_canonical_transcription(native, [], destination)

            saved = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(saved["Provider"], "whisperkit")
        self.assertEqual(saved["Transcription"]["Paragraphs"][0]["Words"][0]["Text"], "test")

    def test_normalized_markdown_names_local_provider(self):
        canonical = canonicalize_whisperkit_result(
            {
                "text": "test",
                "language": "en",
                "segments": [{"start": 0.0, "end": 1.0, "text": "test"}],
            },
            [],
        )

        markdown = normalize_to_markdown(canonical)

        self.assertIn("Transcribed by: WhisperKit (local)", markdown)

    def test_cli_adapter_preserves_native_artifacts_and_writes_canonical_json(self):
        fake_cli_source = """#!/usr/bin/env python3
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
(report_dir / (audio.stem + '.srt')).write_text('1\\n00:00:00,000 --> 00:00:01,000\\nhello world\\n')
print('SPEAKER episode 1 0.000 1.000 hello world <NA> A <NA> <NA>')
"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_cli = tmp_path / "fake-whisperkit"
            fake_cli.write_text(fake_cli_source, encoding="utf-8")
            os.chmod(fake_cli, 0o755)
            audio = tmp_path / "episode.m4a"
            audio.write_bytes(b"fake")
            out_dir = tmp_path / "out"

            artifacts = transcribe_with_whisperkit(
                audio,
                out_dir,
                executable=str(fake_cli),
                model="fake-model",
                language="en",
            )

            canonical = json.loads(artifacts["raw"].read_text(encoding="utf-8"))
            self.assertTrue(artifacts["native_json"].exists())
            self.assertTrue(artifacts["srt"].exists())
            self.assertTrue(artifacts["log"].exists())
            self.assertEqual(
                canonical["Transcription"]["Paragraphs"][0]["SpeakerId"], "A"
            )

    def test_diarization_failure_is_not_silently_reported_as_success(self):
        fake_cli_source = """#!/usr/bin/env python3
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
print('Error during diarization: model download timed out')
"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_cli = tmp_path / "fake-whisperkit"
            fake_cli.write_text(fake_cli_source, encoding="utf-8")
            os.chmod(fake_cli, 0o755)
            audio = tmp_path / "episode.m4a"
            audio.write_bytes(b"fake")

            with self.assertRaisesRegex(WhisperKitError, "RTTM"):
                transcribe_with_whisperkit(
                    audio,
                    tmp_path / "out",
                    executable=str(fake_cli),
                    model="fake-model",
                    language="en",
                    diarization=True,
                )


if __name__ == "__main__":
    unittest.main()
