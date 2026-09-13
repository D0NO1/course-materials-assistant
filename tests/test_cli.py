import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from cli import main


class CliTests(unittest.TestCase):
    def test_extract_command_writes_normalized_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "notes.txt"
            output = Path(temp_dir) / "result.json"
            source.write_text("notes", encoding="utf-8")

            exit_code = main(["extract", str(source), "--output", str(output)])

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "unsupported")

    def test_scan_returns_nonzero_for_missing_course(self):
        with patch("sys.stderr", new_callable=StringIO):
            exit_code = main(["scan", "missing-course"])

        self.assertNotEqual(exit_code, 0)

    def test_learn_writes_session_without_docx_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            (course / "lecture.txt").write_text("lecture", encoding="utf-8")
            exit_code = main(["learn", str(course), "--mode", "preview", "--no-docx"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((course / ".course-assistant" / "learning-session-preview.json").exists())


if __name__ == "__main__":
    unittest.main()
