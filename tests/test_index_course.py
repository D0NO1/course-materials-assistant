import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from index_course import build_index


class IndexCourseTests(unittest.TestCase):
    def test_build_index_uses_relative_posix_paths_for_any_course_location(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "nested" / "MIS-413"
            course.mkdir(parents=True)
            source = course / "week 1" / "lecture.PPTX"
            source.parent.mkdir()
            source.write_bytes(b"slides")

            result = build_index(course)

            self.assertEqual(result["files"][0]["path"], "week 1/lecture.PPTX")
            self.assertEqual(result["course_root"], ".")

    def test_build_index_rejects_missing_course_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "does-not-exist"

            with self.assertRaisesRegex(ValueError, "course directory does not exist"):
                build_index(missing)

    def test_build_index_classifies_and_reuses_unchanged_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413-91 - Systems Analysis"
            course.mkdir()
            (course / "week1.pdf").write_bytes(b"pdf-content")
            (course / "assignment.docx").write_bytes(b"word-content")
            (course / "data.xlsx").write_bytes(b"excel-content")
            (course / "database.accdb").write_bytes(b"access-content")
            (course / "lecture.pptx").write_bytes(b"powerpoint-content")

            first = build_index(course)
            second = build_index(course)

            self.assertEqual({entry["category"] for entry in first["files"]}, {
                "pdf", "word", "excel", "access", "powerpoint"
            })
            self.assertTrue(all(entry["status"] == "indexed" for entry in first["files"]))
            self.assertTrue(all(entry["status"] == "unchanged" for entry in second["files"]))

            index_path = course / ".course-assistant" / "index.json"
            self.assertEqual(json.loads(index_path.read_text(encoding="utf-8"))["course_root"], ".")


    def test_build_index_marks_removed_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            source = course / "reading.pdf"
            source.write_bytes(b"content")

            build_index(course)
            source.unlink()
            result = build_index(course)

            self.assertEqual(result["files"][0]["status"], "missing")


if __name__ == "__main__":
    unittest.main()

