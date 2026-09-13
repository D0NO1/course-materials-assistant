import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from translation_support import translate_text


class TranslationSupportTests(unittest.TestCase):
    def test_translates_common_systems_analysis_sentence(self):
        english = "Scope defines what the project will and will not include."
        chinese = translate_text(english)
        self.assertIn("项目范围", chinese)
        self.assertIn("包含", chinese)
        self.assertNotEqual(english, chinese)

    def test_translates_common_course_terms_and_keeps_english_acronyms(self):
        chinese = translate_text("The SDLC consists of planning, analysis, design, build and test, and maintenance.")
        self.assertIn("SDLC", chinese)
        self.assertIn("规划", chinese)
        self.assertIn("维护", chinese)


if __name__ == "__main__":
    unittest.main()
