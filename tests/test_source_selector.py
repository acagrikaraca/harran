import unittest

from bulletins.source_selector import parse_source_items, select_latest_unprocessed


class SourceSelectorTests(unittest.TestCase):
    def test_select_latest_unprocessed(self):
        items = parse_source_items(
            [
                {
                    "title": "Resmi Marka Bülteni 2026/07",
                    "publish_date": "2026-03-25",
                    "source_url": "https://example.org/7.pdf",
                },
                {
                    "title": "Resmi Marka Bülteni 2026/08",
                    "publish_date": "2026-04-10",
                    "source_url": "https://example.org/8.pdf",
                },
            ]
        )
        selected = select_latest_unprocessed(items, {"2026/07"})
        self.assertIsNotNone(selected)
        self.assertEqual(selected.bulletin_no, "2026/08")

    def test_returns_none_when_all_processed(self):
        items = parse_source_items(
            [
                {
                    "title": "Resmi Marka Bülteni 2026/08",
                    "publish_date": "2026-04-10",
                    "source_url": "https://example.org/8.pdf",
                }
            ]
        )
        selected = select_latest_unprocessed(items, {"2026/08"})
        self.assertIsNone(selected)

    def test_parse_source_items_skips_invalid_rows(self):
        items = parse_source_items(
            [
                {
                    "title": "Resmi Marka Bülteni 2026/09",
                    "publish_date": "2026-04-25",
                    "source_url": "https://example.org/9.pdf",
                },
                {
                    "title": "Eksik Tarih",
                    "source_url": "https://example.org/x.pdf",
                },
                {
                    "title": "Hatalı Tarih 2026/10",
                    "publish_date": "2026-99-99",
                    "source_url": "https://example.org/10.pdf",
                },
            ]
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].bulletin_no, "2026/09")


if __name__ == "__main__":
    unittest.main()
