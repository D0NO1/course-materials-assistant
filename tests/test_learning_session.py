import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from generate_learning_session import SUPPORTED_MODES, generate_learning_session, learning_filename, write_learning_session


MATERIALS = [
    {
        "file": "lecture-01.pdf",
        "format": "pdf",
        "status": "extracted",
        "content": {
            "pages": [
                {"page": 1, "text": "Course objective: explain the SDLC and system scope."},
                {"page": 2, "text": "Scope defines what the project will and will not include."},
            ]
        },
        "warnings": [],
    },
    {
        "file": "assignment.docx",
        "format": "docx",
        "status": "extracted",
        "content": {"paragraphs": [
            {"heading": "Assignment 1", "text": "Submit the project proposal by 2026-10-01."},
            {"heading": "Announcement", "text": "The project proposal is due on 2026-10-03."},
        ]},
        "warnings": [],
    },
    {"file": "database.accdb", "format": "access", "status": "inventory-only", "content": {}, "warnings": ["structure only"]},
]


class LearningSessionTests(unittest.TestCase):
    def test_learning_filenames_are_bilingual(self):
        self.assertEqual(learning_filename("preview"), "01-课前预习-Pre-Class-Preview.json")
        self.assertEqual(learning_filename("exam"), "05-Final-Exam考点复习-Final-Exam-Review.json")

    def test_all_modes_have_bilingual_sections_and_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413"
            course.mkdir()
            for mode in SUPPORTED_MODES:
                result = generate_learning_session(course, MATERIALS, mode)
                self.assertEqual(result["mode"], mode)
                self.assertTrue(result["sections"])
                self.assertIn("sources", result)
                self.assertTrue(any(item.get("en") and item.get("zh") for section in result["sections"] for item in section["items"]))
                self.assertTrue(any(any("\u4e00" <= char <= "\u9fff" for char in item.get("zh", "")) and item.get("zh") != item.get("en") for section in result["sections"] for item in section["items"]))

    def test_preserves_locators_warnings_and_assignment_confidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "assignment")
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertIn("lecture-01.pdf, p. 1", serialized)
            self.assertIn("database.accdb", serialized)
            self.assertIn("2026-10-01", serialized)
            self.assertIn("needs confirmation", serialized)
            output = write_learning_session(course, result)
            self.assertTrue(output.exists())
            self.assertIn(".course-assistant", str(output))

    def test_exam_mode_does_not_claim_guaranteed_questions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "exam")
            text = json.dumps(result, ensure_ascii=False).casefold()
            self.assertNotIn("guaranteed exam question", text)
            self.assertIn("not known", text)

    def test_known_course_gets_concise_real_bilingual_core_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413-91 - Systems Analysis"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "exam")
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertIn("项目范围", serialized)
            self.assertIn("系统开发生命周期", serialized)
            self.assertIn("Course Core", serialized)

    def test_display_english_lines_are_compact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413-91 - Systems Analysis"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "exam")
            for section in result["sections"]:
                for item in section["items"]:
                    self.assertLessEqual(len(item["en"]), 260)


if __name__ == "__main__":
    unittest.main()
