import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from update_course_knowledge import update_knowledge


class UpdateCourseKnowledgeTests(unittest.TestCase):
    def test_update_knowledge_persists_extended_source_collections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            payload = {
                "source_chunks": [{"id": "week1-p1", "text": "SDLC", "source": {"page": 1}}],
                "concept_relations": [{"from": "SDLC", "to": "Analysis", "relation": "contains"}],
                "question_bank": [{"question": "What is SDLC?", "answer": "A development life cycle."}],
            }

            result = update_knowledge(course, payload)

            self.assertIn("source_chunks", result)
            self.assertIn("concept_relations", result)
            self.assertIn("question_bank", result)
            self.assertTrue((course / ".course-assistant" / "question_bank.json").exists())

    def test_update_knowledge_merges_exam_topics_and_writes_course_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            payload = {
                "glossary": [{"term": "SDLC", "meaning": "Systems Development Life Cycle"}],
                "topics": [{"topic": "Scope", "importance": "high", "sources": ["Week 2, p. 10"]}],
                "assignments": [{"name": "Milestone 2", "requirements": ["scope statement"]}],
                "milestones": [{"name": "Milestone 2", "status": "discovered"}],
                "exam_focus": [{"topic": "Feasibility", "why": "Three feasibility questions", "sources": ["Week 2, p. 15"]}],
            }

            result = update_knowledge(course, payload)

            self.assertEqual(result["exam_focus"][0]["topic"], "Feasibility")
            self.assertTrue((course / ".course-assistant" / "glossary.md").exists())
            self.assertTrue((course / ".course-assistant" / "topics.json").exists())
            self.assertTrue((course / ".course-assistant" / "assignments.json").exists())
            self.assertTrue((course / ".course-assistant" / "milestones.json").exists())
            exam_text = (course / ".course-assistant" / "exam-focus.md").read_text(encoding="utf-8")
            self.assertIn("Feasibility", exam_text)

    def test_update_knowledge_deduplicates_by_term_or_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            course = Path(temp_dir) / "course"
            course.mkdir()
            update_knowledge(course, {"glossary": [{"term": "SDLC", "meaning": "old"}]})
            result = update_knowledge(course, {"glossary": [{"term": "SDLC", "meaning": "new"}]})

            self.assertEqual(len(result["glossary"]), 1)
            self.assertEqual(result["glossary"][0]["meaning"], "new")


if __name__ == "__main__":
    unittest.main()
