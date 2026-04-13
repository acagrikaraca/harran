import unittest

from bulletins.parser import clean_extracted_text, parse_bulletin_text


class ParserTests(unittest.TestCase):
    def test_clean_removes_page_lines(self):
        raw = "Sayfa 1\n(210) 2026/123456\n---\n"
        cleaned = clean_extracted_text(raw)
        self.assertNotIn("Sayfa 1", cleaned)
        self.assertNotIn("---", cleaned)

    def test_parse_ignores_corrections_section(self):
        raw = """
        (210) 2026/123456
        (220) 10.04.2026
        (731) A
        (540) TEST
        (511) 35
        (510) reklam

        Düzeltmeler:
        (210) 2026/888888
        """
        records = parse_bulletin_text(raw, bulletin_id="b1")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].application_no, "2026/123456")


if __name__ == "__main__":
    unittest.main()
