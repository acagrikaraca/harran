# Marka Vekili Bülten Tarama Asistanı (MVP Çekirdek)

Bu repo, proje kapsamını kod tarafında ilerleten modüler MVP çekirdeğini içerir.

## Modüller

- `portfolio/importer.py`: Başvuru evrakı metninden portföy kaydı çıkarımı
- `bulletins/parser.py`: Bülten metninden sadece yeni başvuru kayıtlarının ayrıştırılması
- `bulletins/scheduler.py`: Ayın 15'i ve ay sonu/30 kontrol günleri için scheduler kararı
- `bulletins/source_selector.py`: Kaynak bülten listesinden son işlenmemiş bülteni seçme
- `matching/engine.py`: İbare + sınıf + mal/hizmet tabanlı 0-9 skor üretimi
- `app/services.py`: Aktif portföy + yeni başvuru filtreleriyle aday üretim orkestrasyonu
- `app/pipeline.py`: Bülten metnini parse edip kalıcılığa yazan işlem hattı
- `database/sqlite_store.py`: SQLite şema ve upsert/list işlemleri
- `app/models.py`: Portföy, bülten, başvuru ve aday eşleşme veri modelleri
- `app/text_utils.py`: normalize ve sınıf numarası çıkarımı
- `app/demo.py`: uçtan uca demo (scheduler + source selection + parse + persist + matching)

## Çalıştırma

```bash
python app/demo.py
python -m unittest discover -s tests -p 'test_*.py'
```

## Bu sprintte gelen kazanımlar

- Metin tabanlı parser + kural bazlı scoring yanında artık temel persistence (SQLite) mevcut.
- Mükerrer kayıtların önlenmesi için `UNIQUE` + `ON CONFLICT` upsert yaklaşımı eklendi.
- Scheduler kararı ayrı modüle ayrıldı; Şubat gibi kısa aylar için ay sonu kuralı destekleniyor.

## Not

Bu aşama üretim sistemi değildir; MVP omurgasının çalışan ve testlenen çekirdeğidir.


## Paketleme

```bash
python scripts/package_release.py
```

Komut, `dist/` altında zaman damgalı bir zip çıktısı üretir.
