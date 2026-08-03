import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

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


if __name__ == "__main__":
    unittest.main()
