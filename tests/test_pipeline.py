import tempfile
import unittest

from app.pipeline import ingest_bulletin_text
from bulletins.source_selector import BulletinSourceItem
from database.sqlite_store import SQLiteStore
from datetime import date


class PipelineTests(unittest.TestCase):
    def test_skip_when_bulletin_already_processed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SQLiteStore(db_path=f"{tmp_dir}/test.db")
            store.initialize()

            item = BulletinSourceItem(
                bulletin_no="2026/08",
                publish_date=date(2026, 4, 10),
                source_url="https://example.org/8.pdf",
                title="Resmi Marka Bülteni 2026/08",
            )

            text = "(210) 2026/111111\n(540) TEST\n(511) 35\n(731) A"
            first, count1 = ingest_bulletin_text(store, item, text)
            self.assertIsNotNone(first)
            self.assertEqual(count1, 1)

            second, count2 = ingest_bulletin_text(store, item, text)
            self.assertIsNone(second)
            self.assertEqual(count2, 0)
            store.close()


if __name__ == "__main__":
    unittest.main()
