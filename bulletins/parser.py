from __future__ import annotations

import re
from datetime import date
from uuid import uuid4

from app.models import BulletinApplication, ParseConfidence, RecordType
from app.text_utils import extract_class_numbers, normalize_text


def clean_extracted_text(raw_text: str) -> str:
    cleaned = raw_text
    cleaned = re.sub(r"(?m)^\s*Sayfa\s+\d+\s*$", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*-{3,}\s*$", "", cleaned)
    cleaned = re.sub(r"\u00a0", " ", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def split_sections(raw_text: str) -> tuple[str, str]:
    """Return (new_application_part, trailing_non_application_part)."""
    split = re.split(r"\bDüzeltmeler\b\s*:?", raw_text, flags=re.IGNORECASE, maxsplit=1)
    if len(split) == 1:
        return raw_text, ""
    return split[0], split[1]


def segment_by_210(new_applications_text: str) -> list[str]:
    chunks = re.split(r"(?=\(210\))", new_applications_text)
    return [chunk.strip() for chunk in chunks if chunk.strip().startswith("(210)")]


def _extract(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def _confidence(application_no: str, mark_text: str, classes_raw: str, applicant: str) -> ParseConfidence:
    score = 0
    score += int(application_no != "unknown")
    score += int(bool(mark_text))
    score += int(bool(classes_raw))
    score += int(bool(applicant))

    if score >= 4:
        return ParseConfidence.HIGH
    if score >= 2:
        return ParseConfidence.MEDIUM
    return ParseConfidence.LOW


def parse_new_application_record(record_text: str, bulletin_id: str) -> BulletinApplication:
    application_no = _extract(r"\(210\)\s*([0-9]{4}/[0-9]{3,})", record_text) or "unknown"
    application_date_raw = _extract(r"\(220\)\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4})", record_text)
    parsed_date = None
    if application_date_raw:
        d, m, y = application_date_raw.split(".")
        parsed_date = date(int(y), int(m), int(d))

    applicant = _extract(r"\(731\)\s*(.*?)(?:\(540\)|Vekil:|$)", record_text) or ""
    mark_text = _extract(r"\(540\)\s*(.*?)(?:\(511\)|\(510\)|$)", record_text) or ""
    classes_raw = _extract(r"\(511\)\s*(.*?)(?:\(510\)|$)", record_text) or ""
    goods_services = _extract(r"\(510\)\s*(.*)$", record_text) or ""
    agent = _extract(r"Vekil\s*:\s*(.*?)(?:\(540\)|\(511\)|\(510\)|$)", record_text)

    confidence = _confidence(application_no, mark_text, classes_raw, applicant)

    return BulletinApplication(
        id=uuid4().hex,
        bulletin_id=bulletin_id,
        application_no=application_no,
        application_date=parsed_date,
        applicant_name=applicant,
        agent_name=agent,
        mark_text=mark_text,
        normalized_mark_text=normalize_text(mark_text),
        classes=extract_class_numbers(classes_raw),
        goods_services_text=goods_services,
        parse_confidence=confidence,
        record_type=RecordType.NEW_APPLICATION,
    )


def parse_bulletin_text(raw_text: str, bulletin_id: str) -> list[BulletinApplication]:
    cleaned = clean_extracted_text(raw_text)
    applications_part, _ = split_sections(cleaned)
    segments = segment_by_210(applications_part)
    return [parse_new_application_record(segment, bulletin_id) for segment in segments]
