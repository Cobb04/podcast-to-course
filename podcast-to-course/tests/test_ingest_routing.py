import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import ingest_podcast  # noqa: E402
from ingest_podcast import ProviderError, select_provider  # noqa: E402


class ProviderRoutingTests(unittest.TestCase):
    def test_auto_prefers_free_local_provider(self):
        self.assertEqual(
            select_provider("auto", whisperkit_available=True, tingwu_available=True),
            "whisperkit",
        )

    def test_auto_falls_back_to_tingwu(self):
        self.assertEqual(
            select_provider("auto", whisperkit_available=False, tingwu_available=True),
            "tingwu",
        )

    def test_auto_explains_when_no_provider_is_configured(self):
        with self.assertRaisesRegex(ProviderError, "brew install whisperkit-cli"):
            select_provider(
                "auto", whisperkit_available=False, tingwu_available=False
            )

    def test_explicit_provider_must_be_available(self):
        with self.assertRaisesRegex(ProviderError, "WhisperKit"):
            select_provider(
                "whisperkit", whisperkit_available=False, tingwu_available=True
            )


class WhisperKitOptionTests(unittest.TestCase):
    def test_builds_short_asr_prompt_from_metadata_or_explicit_glossary(self):
        self.assertTrue(hasattr(ingest_podcast, "build_asr_prompt"))
        build_asr_prompt = ingest_podcast.build_asr_prompt

        metadata = {
            "title": "对话 LibLib 陈冕",
            "podcast_name": "晚点聊 LateTalk",
        }
        self.assertEqual(
            build_asr_prompt(metadata, None),
            "对话 LibLib 陈冕，晚点聊 LateTalk",
        )
        self.assertEqual(
            build_asr_prompt(metadata, "Evoken，LibLib，Founder"),
            "Evoken，LibLib，Founder",
        )

    def test_cli_accepts_prompt_and_worker_count(self):
        try:
            args = ingest_podcast._parse_args(
                [
                    "--audio-url",
                    "https://example.com/episode.m4a",
                    "--out",
                    "/tmp/output",
                    "--prompt",
                    "LibLib，陈冕",
                    "--concurrent-worker-count",
                    "2",
                ]
            )
        except SystemExit as exc:
            self.fail(f"prompt/worker CLI options should be accepted: {exc}")

        self.assertEqual(args.prompt, "LibLib，陈冕")
        self.assertEqual(args.concurrent_worker_count, 2)


if __name__ == "__main__":
    unittest.main()
