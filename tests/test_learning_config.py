import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from learning_config import load_config, normalize_language_mode, order_bilingual


class LearningConfigTests(unittest.TestCase):
    def test_defaults_and_valid_modes(self):
        self.assertEqual(load_config()["language_mode"], "en-zh")
        self.assertEqual(normalize_language_mode("zh-en"), "zh-en")
        self.assertEqual(order_bilingual("English", "中文", "en-zh"), ["English", "中文"])
        self.assertEqual(order_bilingual("English", "中文", "zh-en"), ["中文", "English"])

    def test_invalid_mode_falls_back_and_single_language_modes(self):
        self.assertEqual(normalize_language_mode("bad"), "en-zh")
        self.assertEqual(order_bilingual("English", "中文", "english-only"), ["English"])
        self.assertEqual(order_bilingual("English", "中文", "chinese-support"), ["中文", "English"])

    def test_loads_json_configuration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(json.dumps({"language_mode": "zh-en", "audience": "international-student"}), encoding="utf-8")
            config = load_config(path)
            self.assertEqual(config["language_mode"], "zh-en")
            self.assertEqual(config["audience"], "international-student")


if __name__ == "__main__":
    unittest.main()
