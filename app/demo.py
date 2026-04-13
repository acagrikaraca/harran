from pathlib import Path
import sys
from datetime import date

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services import find_candidates
from bulletins.scheduler import should_run
from bulletins.source_selector import parse_source_items, select_latest_unprocessed
from database.sqlite_store import SQLiteStore
from portfolio.importer import parse_application_text
from app.pipeline import ingest_bulletin_text


if __name__ == "__main__":
    portfolio_text = """
    Başvuru Numarası: 2026/013298
    Marka Tipi: Şekil + Kelime
    Marka Türü: Ticaret/Hizmet Markası
    Marka Örneği Yazılı İfadesi: bey polat
    Başvuru Sahibi: Örnek İnşaat A.Ş.
    Vekil: Ahmet Vekil
    Sınıf: 37, 35
    """

    bulletin_text = """
    Sayfa 1
    (210) 2026/099999
    (220) 10.04.2026
    (731) Test Yapı Ltd.
    Vekil: Mehmet Vekil
    (540) BEY POLAT PLUS
    (511) 37, 35
    (510) İnşaat hizmetleri, yapı bakım ve onarım.

    Düzeltmeler:
    ...
    """

    source_rows = [
        {
            "title": "Resmi Marka Bülteni 2026/08",
            "publish_date": "2026-04-10",
            "source_url": "https://example.org/bulten-2026-08.pdf",
        }
    ]

    decision = should_run(date.today())
    print(f"Scheduler -> run_today={decision.run_today}, reason={decision.reason}")

    demo_db = Path("data/demo.db")
    if demo_db.exists():
        demo_db.unlink()

    store = SQLiteStore(db_path=str(demo_db))
    store.initialize()

    portfolio_mark = parse_application_text(portfolio_text, source_file="ornek.pdf")
    portfolio_mark.is_user_approved = True
    store.upsert_portfolio_mark(portfolio_mark)

    source_items = parse_source_items(source_rows)
    next_item = select_latest_unprocessed(source_items, store.list_processed_bulletin_nos())
    if not next_item:
        print("İşlenecek yeni bülten bulunamadı.")
        store.close()
        raise SystemExit(0)

    bulletin, parsed_count = ingest_bulletin_text(store, next_item, bulletin_text)
    if not bulletin:
        print("Bu bülten daha önce işlenmiş, tekrar atlandı.")
        store.close()
        raise SystemExit(0)

    print(f"İşlenen bülten: {bulletin.bulletin_no}, parse kayıt sayısı: {parsed_count}")

    applications = []
    # Demo'da karşılaştırma için aynı metni tekrar parse ediyoruz.
    # Üretimde bu kayıtlar veritabanından okunmalı.
    from bulletins.parser import parse_bulletin_text

    applications = parse_bulletin_text(bulletin_text, bulletin_id=bulletin.id)

    candidates = find_candidates([portfolio_mark], applications, minimum_score=3)
    for candidate in candidates:
        print(candidate)

    store.close()
