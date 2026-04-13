from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BulletinSourceItem:
    bulletin_no: str
    publish_date: date
    source_url: str
    title: str


def parse_bulletin_no(title: str) -> str | None:
    match = re.search(r"(\d{4}/\d{1,3})", title)
    return match.group(1) if match else None


def parse_source_items(rows: list[dict[str, str]]) -> list[BulletinSourceItem]:
    """Normalize bulletin metadata rows from external fetch layer.

    Expected keys in each row: title, publish_date (YYYY-MM-DD), source_url.
    Invalid rows are skipped.
    """
    items: list[BulletinSourceItem] = []
    for row in rows:
        try:
            title = row.get("title", "").strip()
            bulletin_no = parse_bulletin_no(title)
            publish_date_raw = row.get("publish_date", "").strip()
            source_url = row.get("source_url", "").strip()
            if not bulletin_no or not publish_date_raw or not source_url:
                continue
            publish_date = date.fromisoformat(publish_date_raw)
            items.append(
                BulletinSourceItem(
                    bulletin_no=bulletin_no,
                    publish_date=publish_date,
                    source_url=source_url,
                    title=title,
                )
            )
        except Exception:
            continue
    return items


def select_latest_unprocessed(
    items: list[BulletinSourceItem],
    processed_bulletin_nos: set[str],
) -> BulletinSourceItem | None:
    eligible = [item for item in items if item.bulletin_no not in processed_bulletin_nos]
    if not eligible:
        return None
    return sorted(eligible, key=lambda item: (item.publish_date, item.bulletin_no), reverse=True)[0]
