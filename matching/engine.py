from __future__ import annotations

from difflib import SequenceMatcher

from app.models import BulletinApplication, CandidateMatch, PortfolioMark
from app.text_utils import normalize_text


def _text_score(a: str, b: str) -> int:
    ratio = SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()
    if ratio >= 0.85:
        return 3
    if ratio >= 0.7:
        return 2
    if ratio >= 0.55:
        return 1
    return 0


def _class_score(a: list[int], b: list[int]) -> int:
    a_set, b_set = set(a), set(b)
    if not a_set or not b_set:
        return 0
    if a_set & b_set:
        return 3
    if any(abs(x - y) <= 1 for x in a_set for y in b_set):
        return 2
    return 0


def _goods_services_score(a: str, b: str) -> int:
    a_tokens = set(normalize_text(a).split())
    b_tokens = set(normalize_text(b).split())
    if not a_tokens or not b_tokens:
        return 0
    overlap = len(a_tokens & b_tokens) / max(1, len(a_tokens | b_tokens))
    if overlap >= 0.35:
        return 3
    if overlap >= 0.2:
        return 2
    if overlap >= 0.1:
        return 1
    return 0


def _label(total_score: int) -> str:
    if total_score <= 2:
        return "düşük öncelik"
    if total_score <= 5:
        return "gözden geçir"
    if total_score <= 7:
        return "güçlü aday"
    return "yüksek öncelik"


def match_record(mark: PortfolioMark, application: BulletinApplication) -> CandidateMatch:
    text = _text_score(mark.mark_text, application.mark_text)
    class_s = _class_score(mark.classes, application.classes)
    goods = _goods_services_score(mark.goods_services_text, application.goods_services_text)
    total = text + class_s + goods

    summary = (
        f"İbare={text}, sınıf={class_s}, mal/hizmet={goods}. "
        f"Toplam skor={total}."
    )

    return CandidateMatch(
        portfolio_mark_id=mark.id,
        bulletin_application_id=application.id,
        text_score=text,
        class_score=class_s,
        goods_services_score=goods,
        total_score=total,
        priority_label=_label(total),
        summary=summary,
    )
