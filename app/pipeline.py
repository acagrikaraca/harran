from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.checksum import md5_text
from app.models import Bulletin
from bulletins.parser import parse_bulletin_text
from bulletins.source_selector import BulletinSourceItem
from database.sqlite_store import SQLiteStore


def ingest_bulletin_text(
    store: SQLiteStore,
    source_item: BulletinSourceItem,
    bulletin_text: str,
    parser_version: str = "v0.3",
) -> tuple[Bulletin | None, int]:
    if store.is_bulletin_processed(source_item.bulletin_no):
        return None, 0

    bulletin = Bulletin(
        id=uuid4().hex,
        bulletin_no=source_item.bulletin_no,
        publish_date=source_item.publish_date,
        source_url=source_item.source_url,
        file_name=f"bulten-{source_item.bulletin_no.replace('/', '-')}.pdf",
        checksum=md5_text(bulletin_text),
        processed_at=datetime.utcnow(),
        process_status="processed",
        parsed_record_count=0,
        unparsed_record_count=0,
        parser_version=parser_version,
    )

    applications = parse_bulletin_text(bulletin_text, bulletin_id=bulletin.id)
    bulletin.parsed_record_count = len(applications)

    store.insert_bulletin(bulletin)
    store.upsert_bulletin_applications(applications)
    return bulletin, len(applications)
