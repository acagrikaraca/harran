from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.models import Bulletin, BulletinApplication, PortfolioMark


class SQLiteStore:
    def __init__(self, db_path: str = "data/trademark_assistant.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def initialize(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS portfolio_marks (
                id TEXT PRIMARY KEY,
                application_no TEXT UNIQUE NOT NULL,
                source_file TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                mark_text TEXT NOT NULL,
                normalized_mark_text TEXT NOT NULL,
                mark_type TEXT,
                mark_kind TEXT,
                applicant_name TEXT,
                agent_name TEXT,
                agent_registry_no TEXT,
                classes_json TEXT NOT NULL,
                goods_services_text TEXT NOT NULL,
                normalized_goods_services_text TEXT NOT NULL,
                parse_confidence TEXT NOT NULL,
                is_user_approved INTEGER NOT NULL,
                is_manually_corrected INTEGER NOT NULL,
                is_active INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bulletins (
                id TEXT PRIMARY KEY,
                bulletin_no TEXT UNIQUE NOT NULL,
                publish_date TEXT NOT NULL,
                source_url TEXT NOT NULL,
                file_name TEXT NOT NULL,
                checksum TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                process_status TEXT NOT NULL,
                parsed_record_count INTEGER NOT NULL,
                unparsed_record_count INTEGER NOT NULL,
                parser_version TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bulletin_applications (
                id TEXT PRIMARY KEY,
                bulletin_id TEXT NOT NULL,
                application_no TEXT NOT NULL,
                application_date TEXT,
                applicant_name TEXT NOT NULL,
                agent_name TEXT,
                mark_text TEXT NOT NULL,
                normalized_mark_text TEXT NOT NULL,
                classes_json TEXT NOT NULL,
                goods_services_text TEXT NOT NULL,
                parse_confidence TEXT NOT NULL,
                record_type TEXT NOT NULL,
                UNIQUE (bulletin_id, application_no)
            );
            """
        )
        self.conn.commit()

    def upsert_portfolio_mark(self, mark: PortfolioMark) -> None:
        self.conn.execute(
            """
            INSERT INTO portfolio_marks (
                id, application_no, source_file, uploaded_at, updated_at, mark_text,
                normalized_mark_text, mark_type, mark_kind, applicant_name, agent_name,
                agent_registry_no, classes_json, goods_services_text,
                normalized_goods_services_text, parse_confidence, is_user_approved,
                is_manually_corrected, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(application_no) DO UPDATE SET
                source_file=excluded.source_file,
                updated_at=excluded.updated_at,
                mark_text=excluded.mark_text,
                normalized_mark_text=excluded.normalized_mark_text,
                mark_type=excluded.mark_type,
                mark_kind=excluded.mark_kind,
                applicant_name=excluded.applicant_name,
                agent_name=excluded.agent_name,
                agent_registry_no=excluded.agent_registry_no,
                classes_json=excluded.classes_json,
                goods_services_text=excluded.goods_services_text,
                normalized_goods_services_text=excluded.normalized_goods_services_text,
                parse_confidence=excluded.parse_confidence,
                is_user_approved=excluded.is_user_approved,
                is_manually_corrected=excluded.is_manually_corrected,
                is_active=excluded.is_active
            """,
            (
                mark.id,
                mark.application_no,
                mark.source_file,
                mark.uploaded_at.isoformat(),
                mark.updated_at.isoformat(),
                mark.mark_text,
                mark.normalized_mark_text,
                mark.mark_type,
                mark.mark_kind,
                mark.applicant_name,
                mark.agent_name,
                mark.agent_registry_no,
                json.dumps(mark.classes, ensure_ascii=False),
                mark.goods_services_text,
                mark.normalized_goods_services_text,
                mark.parse_confidence.value,
                int(mark.is_user_approved),
                int(mark.is_manually_corrected),
                int(mark.is_active),
            ),
        )
        self.conn.commit()

    def insert_bulletin(self, bulletin: Bulletin) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO bulletins (
                id, bulletin_no, publish_date, source_url, file_name, checksum,
                processed_at, process_status, parsed_record_count,
                unparsed_record_count, parser_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bulletin.id,
                bulletin.bulletin_no,
                bulletin.publish_date.isoformat(),
                bulletin.source_url,
                bulletin.file_name,
                bulletin.checksum,
                bulletin.processed_at.isoformat(),
                bulletin.process_status,
                bulletin.parsed_record_count,
                bulletin.unparsed_record_count,
                bulletin.parser_version,
            ),
        )
        self.conn.commit()

    def upsert_bulletin_applications(self, applications: Iterable[BulletinApplication]) -> None:
        self.conn.executemany(
            """
            INSERT INTO bulletin_applications (
                id, bulletin_id, application_no, application_date, applicant_name, agent_name,
                mark_text, normalized_mark_text, classes_json, goods_services_text,
                parse_confidence, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bulletin_id, application_no) DO UPDATE SET
                applicant_name=excluded.applicant_name,
                agent_name=excluded.agent_name,
                mark_text=excluded.mark_text,
                normalized_mark_text=excluded.normalized_mark_text,
                classes_json=excluded.classes_json,
                goods_services_text=excluded.goods_services_text,
                parse_confidence=excluded.parse_confidence,
                record_type=excluded.record_type
            """,
            [
                (
                    application.id,
                    application.bulletin_id,
                    application.application_no,
                    application.application_date.isoformat() if application.application_date else None,
                    application.applicant_name,
                    application.agent_name,
                    application.mark_text,
                    application.normalized_mark_text,
                    json.dumps(application.classes, ensure_ascii=False),
                    application.goods_services_text,
                    application.parse_confidence.value,
                    application.record_type.value,
                )
                for application in applications
            ],
        )
        self.conn.commit()

    def list_active_portfolio_marks(self) -> list[PortfolioMark]:
        rows = self.conn.execute("SELECT * FROM portfolio_marks WHERE is_active = 1").fetchall()
        marks: list[PortfolioMark] = []
        for row in rows:
            payload = dict(row)
            payload["classes"] = json.loads(payload.pop("classes_json"))
            payload["uploaded_at"] = datetime.fromisoformat(payload["uploaded_at"])
            payload["updated_at"] = datetime.fromisoformat(payload["updated_at"])
            payload["is_user_approved"] = bool(payload["is_user_approved"])
            payload["is_manually_corrected"] = bool(payload["is_manually_corrected"])
            payload["is_active"] = bool(payload["is_active"])
            marks.append(PortfolioMark(**payload))
        return marks


    def is_bulletin_processed(self, bulletin_no: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM bulletins WHERE bulletin_no = ? LIMIT 1",
            (bulletin_no,),
        ).fetchone()
        return row is not None

    def list_processed_bulletin_nos(self) -> set[str]:
        rows = self.conn.execute("SELECT bulletin_no FROM bulletins").fetchall()
        return {row["bulletin_no"] for row in rows}

    def close(self) -> None:
        self.conn.close()
