from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SchedulerDecision:
    run_today: bool
    reason: str


def _second_run_day(year: int, month: int) -> int:
    """Run on 30th; for short months use the month's last day."""
    last_day = monthrange(year, month)[1]
    return min(30, last_day)


def should_run(today: date) -> SchedulerDecision:
    second_day = _second_run_day(today.year, today.month)
    if today.day == 15:
        return SchedulerDecision(run_today=True, reason="Aylık birinci kontrol günü (15).")
    if today.day == second_day:
        return SchedulerDecision(
            run_today=True,
            reason=f"Aylık ikinci kontrol günü ({second_day}).",
        )
    return SchedulerDecision(run_today=False, reason="Planlı kontrol günü değil.")
