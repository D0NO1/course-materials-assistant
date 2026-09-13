import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_public_docs_describe_student_learning_contract(self):
        text = "\n".join((ROOT / name).read_text(encoding="utf-8", errors="ignore") for name in ("README.md", "SKILL.md", "agents/openai.yaml"))
        for value in ("preview", "understand", "review", "assignment", "exam", "en-zh", "zh-en", "international-student", "learn"):
            self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()
