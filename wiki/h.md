# Sıcak Bellek — Mikrobiyal AIoT

**Max 500 kelime | Güncelleme: 2026-04-28**

---

## Proje Durumu

**Faz:** 1 — Simülasyon & Makale taslağı tamamlandı  
**Aktif sorun:** Fiziksel prototip henüz yapılmadı (Faz 2 başlamadı)  
**Engel:** Öğrenci sayısı ve rol dağılımı belirsiz

---

## Bu Oturum Yapılanlar (2026-04-28)

- ✅ `paper/generate_figures.py` — 8 figür tam düzeltildi (300 DPI, MDPI uyumlu)
  - Fig 1: Mimari katman diyagramı (label yerleşimi düzeltildi)
  - Fig 2: Substrat simülasyonu (güç yoğunluğu + SoC fiziği düzeltildi)
  - Fig 6: Karar modeli SoC dengesi sağlandı (0'a düşmüyor)
  - Fig 7: Bar etiket çakışması giderildi
  - Fig 8: Heatmap metin taşması + x-eksen düzeltildi
- ✅ `paper/Sensors_MFC_AIoT_2026.pdf` — 19 sayfa, tüm figürler yerinde
- ✅ `/hakem` skill oluşturuldu (`~/.claude/commands/hakem.md`)
- ✅ `references/dergi-bilgi.md` — 8 dergi kayıtlı self-updating bilgi tabanı

---

## Makale Durumu

**Dosya:** `paper/Sensors_MFC_AIoT_2026.pdf`  
**Hedef dergi:** MDPI Sensors (IF ~3.9, Q2)  
**Durum:** Taslak — revision gerekli (bkz. hakem raporu)  
**Kritik eksikler:**
- Fiziksel prototip yok → simülasyon-only makale için Limitations bölümü zorunlu
- Gerçek ölçüm verisi yok → kalibrasyonun literatür kaynakları eklenebilir
- Karşılaştırma tablosu (related work) yeterince güçlendirilmeli

---

## Kritik Kararlar Bekliyor

1. **Bakteri kaynağı:** Çamur / atık su / toprak
2. **İletişim protokolü:** LoRa vs. WiFi mesh
3. **ML platformu:** Edge (ESP32 TinyML) vs. Cloud (RPi gateway)
4. **Elektrot malzemesi:** Grafit kumaş vs. Karbon keçe

---

## Bütçe Özeti

| Kategori | Tahmini TL |
|----------|-----------|
| MFC malzemeleri | 800–1.200 TL |
| Elektronik | 1.500–2.000 TL |
| Sensörler | 600–900 TL |
| **TOPLAM** | **~2.900–4.100 TL** |

---

## Hemen Yapılacaklar

- [ ] Makaleye Limitations bölümü ekle
- [ ] Related Work karşılaştırma tablosu güçlendir
- [ ] Bakteri kaynağı kararı ver → mfc-insaati.md yaz
- [ ] Öğrenci rolleri belirle → proje-plani.md güncelle
- [ ] Fiziksel prototip Faz 2'yi başlat

---

## Bilgi Boşlukları

- Nafion 117 Türkiye'de satılıyor mu? (araştır)
- Gerçek MFC ölçüm verisiyle simülasyon kalibrasyonu yapılabilir mi?
- ESP32 + TinyML anomali modeli örnek kodu lazım

---

**Sonraki Güncelleme:** Faz 2 başladığında veya makale revize edildiğinde
