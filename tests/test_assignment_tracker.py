import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from generate_assignment_tracker import generate_assignment_tracker


class AssignmentTrackerTests(unittest.TestCase):
    def test_tracker_preserves_conflicting_due_dates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            extracted = [
                {
                    "file": "syllabus.docx",
                    "format": "word",
                    "content": {"paragraphs": [{"text": "Milestone 2 due 2026-10-15"}]},
                    "locators": [{"type": "heading", "number": 1, "label": "Assignments"}],
                },
                {
                    "file": "announcement.docx",
                    "format": "word",
                    "content": {"paragraphs": [{"text": "Milestone 2 due 2026-10-20"}]},
                    "locators": [{"type": "paragraph", "number": 4, "label": "Milestone 2"}],
                },
            ]

            result = generate_assignment_tracker(course, extracted)

            self.assertEqual(result["assignments"][0]["name"], "Milestone 2")
            self.assertEqual(result["assignments"][0]["due_dates"], ["2026-10-15", "2026-10-20"])
            self.assertTrue(result["assignments"][0]["conflicts"])
            self.assertTrue((course / ".course-assistant" / "assignment-tracker.json").exists())


if __name__ == "__main__":
    unittest.main()
