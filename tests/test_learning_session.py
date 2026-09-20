import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from generate_learning_session import SUPPORTED_MODES, _text_items, generate_learning_session, learning_filename, write_learning_session


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
        self.assertEqual(learning_filename("preview"), "01-课前预习-双语.json")
        self.assertEqual(learning_filename("understand"), "02-课堂理解-双语.json")
        self.assertEqual(learning_filename("review"), "03-课后复习-双语.json")
        self.assertEqual(learning_filename("assignment"), "04-作业任务-双语.json")
        self.assertEqual(learning_filename("exam"), "05-期末考试考点复习-双语.json")

    def test_generated_session_uses_the_same_clear_public_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413-91 - Systems Analysis"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "exam")
            self.assertEqual(result["output_filename"], "05-期末考试考点复习-双语")

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

    def test_exam_mode_uses_concept_cards_instead_of_slide_dumps(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-413-91 - Systems Analysis"
            course.mkdir()
            result = generate_learning_session(course, MATERIALS, "exam")
            exam_items = result["sections"][-1]["items"]
            first = exam_items[0]
            self.assertEqual(first["en"], "Project scope defines the boundary of the system-analysis work.")
            self.assertIn("项目范围", first["zh"])
            self.assertNotIn("Priority topic:", first["en"])

    def test_slide_text_removes_duplicate_title_and_footer_noise(self):
        material = {
            "file": "security.pptx",
            "content": {
                "slides": [{
                    "slide": 5,
                    "title": "Today's Attacks (part 1 of 5)",
                    "text": [
                        "Today's Attacks (part 1 of 5)",
                        "Attacks directed at point-of-sale systems",
                        "5",
                        "Security Awareness, 5th Edition",
                    ],
                    "notes": "Today's Attacks\n\nAttacks directed at point-of-sale systems",
                }]
            },
        }
        text, _ = _text_items(material)[0]
        self.assertEqual(text.count("Today's Attacks"), 1)
        self.assertNotIn("Security Awareness, 5th Edition", text)
        self.assertNotIn(" 5 ", f" {text} ")

    def test_known_course_modes_use_concise_bilingual_cards(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "MIS-301-91 - Practical Computer Security"
            course.mkdir()
            messy_materials = MATERIALS + [{
                "file": "security.pptx",
                "format": "pptx",
                "status": "extracted",
                "content": {
                    "slides": [{
                        "slide": 1,
                        "title": "Understanding the Importance of Information Security",
                        "text": [
                            "Understanding the Importance of Information Security",
                            "Goals of information security include preventing data theft, thwarting identity theft, avoiding legal consequences, maintaining productivity, and foiling cyberterrorism.",
                        ],
                    }]
                },
                "warnings": [],
            }, {
                "file": "assignment.docx",
                "format": "docx",
                "status": "extracted",
                "content": {"paragraphs": [{
                    "heading": "Project 1",
                    "text": "For this assignment use the PowerPoint presentations, textbook, notes, and Web to create a new presentation that emphasizes the essence of practical computer security and present it in class before posting it on D2L.",
                }]},
                "warnings": [],
            }]
            for mode in ("preview", "understand", "review", "assignment", "exam"):
                result = generate_learning_session(course, messy_materials, mode)
                items = result["sections"][-1]["items"]
                for item in items:
                    self.assertNotIn("Priority topic:", item.get("en", ""))
                    self.assertNotIn("本段概括", item.get("zh", ""))
                    self.assertNotIn("本段介绍课程中的相关内容", item.get("zh", ""))
                    self.assertLessEqual(len(item.get("en", "")), 220)
                    self.assertTrue(any("\u4e00" <= char <= "\u9fff" for char in item.get("zh", "")))


if __name__ == "__main__":
    unittest.main()
