import unittest
from datetime import datetime

from app.models import BulletinApplication, ParseConfidence, PortfolioMark, RecordType
from app.text_utils import normalize_text
from matching.engine import match_record


class MatchingTests(unittest.TestCase):
    def test_normalize_text(self):
        self.assertEqual(normalize_text("Şekil + Kelime!!"), "sekil kelime")

    def test_match_record_scores(self):
        mark = PortfolioMark(
            id="p1",
            application_no="2026/1",
            source_file="a.pdf",
            uploaded_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            mark_text="bey polat",
            normalized_mark_text="bey polat",
            classes=[37],
            goods_services_text="insaat bakim onarim",
            normalized_goods_services_text="insaat bakim onarim",
            parse_confidence=ParseConfidence.HIGH,
        )

        app = BulletinApplication(
            id="b1",
            bulletin_id="x",
            application_no="2026/2",
            application_date=None,
            applicant_name="ABC",
            agent_name=None,
            mark_text="BEY POLAT PLUS",
            normalized_mark_text="bey polat plus",
            classes=[37],
            goods_services_text="insaat ve onarim hizmetleri",
            parse_confidence=ParseConfidence.HIGH,
            record_type=RecordType.NEW_APPLICATION,
        )

        candidate = match_record(mark, app)
        self.assertGreaterEqual(candidate.total_score, 6)
        self.assertIn(candidate.priority_label, {"güçlü aday", "yüksek öncelik"})


if __name__ == "__main__":
    unittest.main()
