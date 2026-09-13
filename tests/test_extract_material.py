import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from extract_material import extract_material, extract_many


class ExtractMaterialTests(unittest.TestCase):
    def test_unsupported_file_returns_explicit_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "notes.txt"
            path.write_text("notes", encoding="utf-8")

            result = extract_material(path)

            self.assertEqual(result["format"], "other")
            self.assertEqual(result["status"], "unsupported")
            self.assertEqual(result["file"], "notes.txt")
            self.assertIsInstance(result["warnings"], list)

    def test_missing_file_returns_error_without_throwing(self):
        result = extract_material(Path("does-not-exist.pptx"))

        self.assertEqual(result["status"], "error")
        self.assertTrue(result["warnings"])

    def test_extract_many_returns_json_serializable_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = []
            for name in ("one.txt", "two.bin"):
                path = Path(temp_dir) / name
                path.write_bytes(b"content")
                paths.append(path)

            results = extract_many(paths)

            self.assertEqual(len(results), 2)
            json.dumps(results)


if __name__ == "__main__":
    unittest.main()
