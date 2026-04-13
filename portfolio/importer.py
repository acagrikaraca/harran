from __future__ import annotations

import re
from datetime import datetime
from uuid import uuid4

from app.models import ParseConfidence, PortfolioMark
from app.text_utils import extract_class_numbers, normalize_text


FIELD_PATTERNS = {
    "application_no": r"Başvuru\s+Numarası\s*:?\s*([0-9]{4}/[0-9]{3,})",
    "mark_type": r"Marka\s+Tipi\s*:?\s*(.+)",
    "mark_kind": r"Marka\s+Türü\s*:?\s*(.+)",
    "mark_text": r"Marka\s+Örneği\s+Yazılı\s+İfadesi\s*:?\s*(.+)",
    "applicant_name": r"Başvuru\s+Sahibi\s*:?\s*(.+)",
    "agent_name": r"Vekil\s*:?\s*(.+)",
    "agent_registry_no": r"Vekil\s+Sicil\s+No\s*:?\s*([0-9]+)",
    "classes_line": r"Sınıf\s*:?\s*(.+)",
}


def _capture(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_application_text(raw_text: str, source_file: str) -> PortfolioMark:
    now = datetime.utcnow()

    application_no = _capture(FIELD_PATTERNS["application_no"], raw_text) or f"unknown/{uuid4().hex[:8]}"
    mark_text = _capture(FIELD_PATTERNS["mark_text"], raw_text) or ""
    classes_line = _capture(FIELD_PATTERNS["classes_line"], raw_text) or ""

    confidence = ParseConfidence.HIGH if mark_text and application_no and classes_line else ParseConfidence.MEDIUM

    return PortfolioMark(
        id=uuid4().hex,
        application_no=application_no,
        source_file=source_file,
        uploaded_at=now,
        updated_at=now,
        mark_text=mark_text,
        normalized_mark_text=normalize_text(mark_text),
        mark_type=_capture(FIELD_PATTERNS["mark_type"], raw_text),
        mark_kind=_capture(FIELD_PATTERNS["mark_kind"], raw_text),
        applicant_name=_capture(FIELD_PATTERNS["applicant_name"], raw_text),
        agent_name=_capture(FIELD_PATTERNS["agent_name"], raw_text),
        agent_registry_no=_capture(FIELD_PATTERNS["agent_registry_no"], raw_text),
        classes=extract_class_numbers(classes_line),
        goods_services_text=raw_text,
        normalized_goods_services_text=normalize_text(raw_text),
        parse_confidence=confidence,
    )
