import tempfile
import unittest
from datetime import datetime

from app.models import BulletinApplication, ParseConfidence, PortfolioMark, RecordType
from app.services import find_candidates
from database.sqlite_store import SQLiteStore


class StoreAndServiceTests(unittest.TestCase):
    def test_upsert_and_list_active_marks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SQLiteStore(db_path=f"{tmp_dir}/test.db")
            store.initialize()

            mark = PortfolioMark(
                id="m1",
                application_no="2026/100",
                source_file="x.pdf",
                uploaded_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                mark_text="bey polat",
                normalized_mark_text="bey polat",
                classes=[37],
                goods_services_text="insaat",
                normalized_goods_services_text="insaat",
                parse_confidence=ParseConfidence.HIGH,
                is_active=True,
            )
            store.upsert_portfolio_mark(mark)
            marks = store.list_active_portfolio_marks()

            self.assertEqual(len(marks), 1)
            self.assertEqual(marks[0].application_no, "2026/100")
            store.close()

    def test_find_candidates_filters_record_type(self):
        mark = PortfolioMark(
            id="m1",
            application_no="2026/100",
            source_file="x.pdf",
            uploaded_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            mark_text="bey polat",
            normalized_mark_text="bey polat",
            classes=[37],
            goods_services_text="insaat onarim",
            normalized_goods_services_text="insaat onarim",
            parse_confidence=ParseConfidence.HIGH,
            is_active=True,
        )

        app_new = BulletinApplication(
            id="a1",
            bulletin_id="b1",
            application_no="2026/200",
            application_date=None,
            applicant_name="A",
            agent_name=None,
            mark_text="bey polat plus",
            normalized_mark_text="bey polat plus",
            classes=[37],
            goods_services_text="insaat",
            parse_confidence=ParseConfidence.HIGH,
            record_type=RecordType.NEW_APPLICATION,
        )

        app_correction = BulletinApplication(
            id="a2",
            bulletin_id="b1",
            application_no="2026/201",
            application_date=None,
            applicant_name="B",
            agent_name=None,
            mark_text="bey polat",
            normalized_mark_text="bey polat",
            classes=[37],
            goods_services_text="insaat",
            parse_confidence=ParseConfidence.HIGH,
            record_type=RecordType.CORRECTION,
        )

        matches = find_candidates([mark], [app_new, app_correction], minimum_score=0)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].bulletin_application_id, "a1")


if __name__ == "__main__":
    unittest.main()
