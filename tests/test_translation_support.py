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

    def test_long_source_becomes_concise_chinese_support_without_full_english_copy(self):
        english = "Course objectives explain the SDLC, scope, requirements, data-flow diagrams, entity-relationship diagrams, use cases, design, testing, and maintenance. " * 4
        chinese = translate_text(english)
        self.assertIn("学习目标", chinese)
        self.assertLess(len(chinese), 180)
        self.assertNotIn("Course objectives explain the SDLC", chinese)

    def test_security_attack_topic_gets_specific_chinese_summary(self):
        english = (
            "Today’s Attacks (part 1 of 5) Attacks directed at point-of-sale systems "
            "called memory-scrapers steal payment card numbers. Healthcare information "
            "can also be used for identity theft and billing fraud."
        )
        chinese = translate_text(english)
        self.assertIn("销售点", chinese)
        self.assertIn("支付卡", chinese)
        self.assertNotIn("本段概括课程材料的主要内容，重点是。", chinese)

    def test_database_topic_gets_concept_explanation(self):
        english = "Data versus Information Data are raw facts; information is processed data with meaning for the user."
        chinese = translate_text(english)
        self.assertIn("原始事实", chinese)
        self.assertIn("有意义", chinese)
        self.assertNotIn("原文关键词", chinese)

    def test_unmatched_sentence_is_flagged_honestly_without_placeholder_translation(self):
        english = "The architecture should support secure integration across departments and provide clear auditability."
        chinese = translate_text(english)
        self.assertIn("未匹配到可靠的本地翻译", chinese)
        self.assertNotIn("本段介绍课程中的相关内容", chinese)
        self.assertNotIn("原文关键词", chinese)


if __name__ == "__main__":
    unittest.main()
