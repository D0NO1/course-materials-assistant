import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from index_course import _category


class FormatRoutingTests(unittest.TestCase):
    def test_supported_extensions_are_case_insensitive(self):
        self.assertEqual(_category(Path("lecture.PDF")), "pdf")
        self.assertEqual(_category(Path("slides.PpTx")), "powerpoint")
        self.assertEqual(_category(Path("data.XLSX")), "excel")
        self.assertEqual(_category(Path("database.MDB")), "access")

    def test_unknown_extensions_are_inventory_only(self):
        self.assertEqual(_category(Path("notes.txt")), "other")


if __name__ == "__main__":
    unittest.main()
