import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from generate_exam_review import generate_exam_review


class ExamReviewTests(unittest.TestCase):
    def test_exam_review_groups_topics_and_preserves_bilingual_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            metadata = course / ".course-assistant"
            metadata.mkdir(parents=True)
            (metadata / "topics.json").write_text(
                json.dumps([
                    {"topic": "Scope", "importance": "high", "sources": ["Week 2, p. 10"]},
                    {"topic": "Maintenance", "importance": "medium", "sources": ["Week 10, p. 3"]},
                ]), encoding="utf-8"
            )
            (metadata / "exam_focus.json").write_text(
                json.dumps([{
                    "topic": "Scope",
                    "why": "Defines boundaries",
                    "why_zh": "定义项目边界",
                    "must_know": "Inclusions and exclusions",
                    "must_know_zh": "项目包含和不包含的内容",
                    "sources": ["Week 2, p. 10"],
                }]), encoding="utf-8"
            )

            result = generate_exam_review(course)

            self.assertEqual(result["high_priority"][0]["topic"], "Scope")
            self.assertEqual(result["high_priority"][0]["why_zh"], "定义项目边界")
            self.assertTrue((metadata / "final-exam-review.json").exists())
            self.assertTrue((metadata / "final-exam-review.md").exists())


if __name__ == "__main__":
    unittest.main()
