---
title: Proje Planı — Mikrobiyal AIoT Sensör Ağı
created: 2026-04-25
updated: 2026-04-25
tags: [proje, plan, zaman-çizelgesi, milestones]
level: proje
---

# Proje Planı

## Özet
BİLSEM PROJE seviyesi çalışması. Toprak/su ortamındaki bakterilerin ürettiği elektrikle çalışan, yapay zeka destekli otonom çevre sensör ağı tasarlama ve prototipleme. Ticari güç kaynağına ihtiyaç duymadan sürekli veri toplar.

---

## Proje Hedefi

**Ana hedef:** En az 1 sensör nodunu, yalnızca MFC enerjisiyle, kesintisiz 48 saat çalıştırmak ve çevre verisi toplamak.

**Başarı kriterleri:**
- [ ] MFC çıkış gücü ≥ 500 µW (500 mW/m² yüzey alanı)
- [ ] ESP32 deep-sleep modunda ortalama tüketim ≤ 1 mA
- [ ] 48 saatlik otonom çalışma (pil takviyesi olmadan)
- [ ] Anomali tespit doğruluğu ≥ %85 (test seti üzerinde)
- [ ] En az 3 çevresel parametrenin eş zamanlı ölçümü

---

## Faz Zaman Çizelgesi

| Faz | Konu | Süre | Çıktı |
|-----|------|------|-------|
| **Faz 0** | Kurulum, araştırma, malzeme temini | 1 hafta | Malzeme listesi onaylanmış |
| **Faz 1** | MFC prototip yapımı | 2–3 hafta | Çalışan MFC hücresi |
| **Faz 2** | Sensör node montajı | 2 hafta | ESP32 + sensörler entegre |
| **Faz 3** | Yazılım geliştirme | 3–4 hafta | Firmware + ML modeli |
| **Faz 4** | Saha testi ve kalibrasyon | 2 hafta | 48 saat test raporu |
| **Faz 5** | Raporlama ve sunum | 1 hafta | Final raporu + sunum |

**Toplam tahmini süre:** 11–13 hafta (PROJE seviyesi: 72–144 saat uyumlu)

---

## Ekip Rolleri

| Rol | Sorumluluk |
|-----|-----------|
| **Biyoloji / Kimya** | MFC bakteri kültürü, elektrot hazırlama, kimyasal güvenlik |
| **Elektronik / Donanım** | Devre tasarımı, sensör entegrasyon, güç yönetimi |
| **Yazılım / Veri** | ESP32 firmware, ML modeli, dashboard |
| **Proje Koordinatör** | Zaman takibi, raporlama, sunum |

*(Öğrenci sayısına göre roller birleştirilebilir)*

---

## Kilometre Taşları (Milestones)

```
M1: MFC açık devre voltajı ≥ 0.3V ölçüldü
M2: ESP32 + sensör node MFC ile güçleniyor
M3: LoRa veri iletimi çalışıyor
M4: ML modeli ilk anomali tespiti yaptı
M5: 48 saatlik kesintisiz otonom çalışma tamamlandı
```

---

## Risk Analizi

| Risk | Olasılık | Çözüm |
|------|----------|-------|
| MFC yeterli güç üretemiyor | Orta | Hücre sayısını artır veya süper kapasitör büyüt |
| Bakteri kültürü gelişmiyor | Düşük | Farklı organik substrat dene |
| LoRa bağlantı sorunu | Düşük | WiFi yedek protokolü |
| Bütçe aşımı | Orta | Malzeme-listesi.md'deki ucuz alternatiflere geç |

---

## Bağlantılar
- [[guvenlik]] — 🚨 Faz 1 öncesi mutlaka oku
- [[sistem-mimarisi]] — teknik mimari detayları
- [[malzeme-listesi]] — Faz 0 için alım listesi
- [[mfc-temelleri]] — MFC'yi anlamak için
