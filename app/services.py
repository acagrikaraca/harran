from __future__ import annotations

from app.models import BulletinApplication, CandidateMatch, PortfolioMark, RecordType
from matching.engine import match_record


def find_candidates(
    portfolio_marks: list[PortfolioMark],
    bulletin_applications: list[BulletinApplication],
    minimum_score: int = 3,
) -> list[CandidateMatch]:
    matches: list[CandidateMatch] = []

    for mark in portfolio_marks:
        if not mark.is_active:
            continue
        for application in bulletin_applications:
            if application.record_type is not RecordType.NEW_APPLICATION:
                continue
            candidate = match_record(mark, application)
            if candidate.total_score >= minimum_score:
                matches.append(candidate)

    return sorted(matches, key=lambda item: item.total_score, reverse=True)
