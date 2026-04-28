# CLAUDE.md — Mikrobiyal AIoT Sensör Ağı Projesi

## Proje
**Mikrobiyal Enerji Hasadı ile Çalışan Yapay Zeka Destekli Otonom Çevre Sensör Ağı**  
Seviye: PROJE | Hedef: Biyolojik enerji kaynağıyla kendi kendine çalışan akıllı sensör ağı

## Yapı
```
simulation/     → Python fizik modelleri (dijital ikiz)
  mfc_model.py         — Basit MFC enerji üretim modeli
  energy_storage.py    — Süper kapasitör modeli
  sensor_node.py       — Node davranış modeli
  mfc_simulation.py    — Detaylı fizik simülasyonu
  energy_model.py      — Enerji bütçe analizi
  transmission_model.py— LoRa link bütçesi
ai/             → Makine öğrenmesi modelleri
  decision_model.py    — RandomForest TX karar modeli
  train.py             — Isolation Forest anomali eğitimi
  dataset.csv          — Eğitim verisi (gerçek veya sentetik)
firmware/       → ESP32 Arduino kodu
  esp32_main.ino       — Ana döngü (deep sleep + TX)
  lora_driver.h/.cpp   — LoRa sürücü sarmalayıcı
main.py         → Uçtan uca simülasyon giriş noktası
wiki/           → İşlenmiş bilgi sayfaları
wiki/index.md   → Tüm sayfaların listesi
wiki/h.md       → Sıcak bellek, max 500 kelime
raw/            → Ham girdiler (PDF, notlar, ölçüm verileri)
```

## Geliştirme Akışı
```
Simülasyon → AI → Firmware → Donanım → Saha testi → Dokümantasyon
```

## Parent Kurallar
Bu proje `bilsem_beyin/CLAUDE.md` kurallarını devralır.  
Çelişki varsa bu dosya geçerlidir.

---

## Komutlar

- `/işle` — raw/ klasöründeki yeni dosyaları wiki sayfasına dönüştür
- `/güncelle` — wiki/index.md ve wiki/h.md yenile
- `/malzeme [bileşen]` — malzeme-listesi.md güncelle, fiyat/tedarikçi ekle
- `/güvenlik [konu]` — guvenlik.md kontrol listesi üret
- `/durum` — proje istatistikleri (tamamlanan faz, aktif sorunlar)
- `/haftalık` — bu haftanın ilerleme raporu
- `/test [faz]` — test protokolü ve sonuçları kaydet
- `/kalibrasyon` — sensör kalibrasyon notlarını güncelle

---

## Wiki Sayfaları

| Dosya | Konu | Durum |
|-------|------|-------|
| proje-plani.md | Faz planı, roller, hedefler | ✅ |
| sistem-mimarisi.md | Blok diyagram, katmanlar | ✅ |
| malzeme-listesi.md | BOM, tedarikçiler, bütçe | ✅ |
| mfc-temelleri.md | MFC kavramı (3 seviye) | ✅ |
| guvenlik.md | Kimyasal + elektrik güvenliği | ✅ |
| mfc-insaati.md | Yapım rehberi | ⏳ ekle |
| sensor-node.md | ESP32 + sensör montajı | ⏳ ekle |
| yazilim.md | Firmware + ML kod | ⏳ ekle |
| saha-testi.md | Saha konuşlandırma + kalibrasyon | ⏳ ekle |

---

## Güvenlik Önceliği
🚨 Bakteri kültürü, kimyasal reaktif veya elektrik konularında
**guvenlik.md HER ZAMAN İLK** okunacak sayfa. Atlama.

---

## Simülasyonu Çalıştır
```bash
pip install -r requirements.txt
python main.py                     # Hızlı test (1000 adım)
python main.py --steps 5000        # Uzun simülasyon
python simulation/mfc_simulation.py   # Detaylı fizik analizi
python simulation/energy_model.py     # Bütçe matrisi
python simulation/transmission_model.py  # LoRa menzil analizi
python ai/train.py                    # Anomali modelini eğit
```

---

**Oluşturma:** 2026-04-25 | **Güncelleme:** 2026-04-26 | **Versiyon:** 2.0
