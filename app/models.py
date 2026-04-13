from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class ParseConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecordType(str, Enum):
    NEW_APPLICATION = "yeni_basvuru"
    CORRECTION = "duzeltme"
    ANNOTATION = "serh"
    OTHER = "diger"


@dataclass
class PortfolioMark:
    id: str
    application_no: str
    source_file: str
    uploaded_at: datetime
    updated_at: datetime
    mark_text: str
    normalized_mark_text: str
    mark_type: Optional[str] = None
    mark_kind: Optional[str] = None
    applicant_name: Optional[str] = None
    agent_name: Optional[str] = None
    agent_registry_no: Optional[str] = None
    classes: List[int] = field(default_factory=list)
    goods_services_text: str = ""
    normalized_goods_services_text: str = ""
    parse_confidence: ParseConfidence = ParseConfidence.MEDIUM
    is_user_approved: bool = False
    is_manually_corrected: bool = False
    is_active: bool = True


@dataclass
class Bulletin:
    id: str
    bulletin_no: str
    publish_date: date
    source_url: str
    file_name: str
    checksum: str
    processed_at: datetime
    process_status: str
    parsed_record_count: int
    unparsed_record_count: int
    parser_version: str


@dataclass
class BulletinApplication:
    id: str
    bulletin_id: str
    application_no: str
    application_date: Optional[date]
    applicant_name: str
    agent_name: Optional[str]
    mark_text: str
    normalized_mark_text: str
    classes: List[int]
    goods_services_text: str
    parse_confidence: ParseConfidence
    record_type: RecordType


@dataclass
class CandidateMatch:
    portfolio_mark_id: str
    bulletin_application_id: str
    text_score: int
    goods_services_score: int
    class_score: int
    total_score: int
    priority_label: str
    summary: str
