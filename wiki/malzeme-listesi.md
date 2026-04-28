---
title: Malzeme Listesi ve Bütçe
created: 2026-04-25
updated: 2026-04-25
tags: [malzeme, bütçe, tedarik, bom, türkiye]
level: proje
---

# Malzeme Listesi — Mikrobiyal AIoT Sensör Ağı

## Özet
Tek sensör node için tahmini bütçe: **2.900–4.100 TL** (Nisan 2026 fiyatları). Tüm fiyatlar TL, Türkiye tedarikçileri öncelikli. Her kategoride ucuz alternatif var.

---

## 🚨 Güvenlik Notu
Kimyasal malzemeleri almadan önce [[guvenlik]] sayfasını oku.

---

## KATEGORİ 1: MFC Bileşenleri

| Malzeme | Amaç | Fiyat (TL) | Tedarikçi | Alternatif |
|---------|------|-----------|-----------|------------|
| Grafit kumaş (10×10 cm) | Anot elektrodu | 150–250 | Amazon TR / AliExpress | Grafit çubuk veya kalem ucu (5 TL) |
| Karbon keçe (10×10 cm) | Anot alternatifi | 80–120 | Robotistan | — |
| Paslanmaz çelik ağ | Katot desteği | 50–80 | Demir bayii | Grafit çubuk |
| Nafion 117 (10×10 cm) | Proton membranı | 300–500 | İthalat / AliExpress | Tuz köprüsü (10 TL) |
| PVC boru (Ø50mm, 20cm) | MFC gövdesi | 20–30 | Yapı marketi | Plastik şişe |
| Sodyum asetat (100g) | Bakteri substraı | 50–80 | Eczane / kimyasal sat. | Şeker çözeltisi |
| Epoksi yapıştırıcı | Sızdırmazlık | 30–50 | Yapı marketi | Silikon |
| **Alt toplam MFC** | | **680–1.110 TL** | | |

**Tuz köprüsü alternatifi (Nafion yerine):**
- Tuzlu agar tüp (tuz + agar tozu, 20–30 TL) — verim %30 düşük ama çok ucuz

---

## KATEGORİ 2: Elektronik (Güç + MCU)

| Malzeme | Amaç | Fiyat (TL) | Tedarikçi | Alternatif |
|---------|------|-----------|-----------|------------|
| ESP32 DevKit v1 | Ana mikrokontrolör | 120–180 | Robotistan / Direkt Drone | ESP8266 (WiFi only, 80 TL) |
| BQ25570 değerlendirme kartı | Enerji hasat IC | 300–500 | Mouser / Digi-Key (ithalat) | LTC3108 (benzer) |
| Süper kapasitör 1F 2.7V | Enerji tamponu | 30–60 | Robotistan | Küçük LiPo (3.7V) |
| LDO regülatör (AMS1117-3.3) | 3.3V sabit çıkış | 10–20 | Robotistan | — |
| LoRa modülü (Ra-02 433MHz) | Veri iletimi | 120–200 | Robotistan / AliExpress | ESP32 dahili WiFi |
| PCB breadboard (800 delikli) | Prototip devre | 25–40 | Robotistan | — |
| Jumper kablo seti | Bağlantı | 30–50 | Robotistan | — |
| Multimetre | Ölçüm ve test | 150–300 | Teknosa | Okulda varsa gerekmez |
| **Alt toplam elektronik** | | **785–1.350 TL** | | |

---

## KATEGORİ 3: Sensörler

| Malzeme | Ölçüm | Fiyat (TL) | Tedarikçi | Alternatif |
|---------|-------|-----------|-----------|------------|
| Kapasitif toprak nemi sensörü | Nem (0–100%) | 35–60 | Robotistan | Direnç bazlı (15 TL, paslanır) |
| DS18B20 sıcaklık sensörü | Sıcaklık (-55–125°C) | 25–40 | Robotistan | LM35 (20 TL) |
| Analog pH sensör modülü | pH (0–14) | 150–250 | AliExpress / Direkt Drone | Litmus kağıdı (manuel) |
| MQ-135 gaz sensörü | CO₂/NH₃/VOC | 40–70 | Robotistan | DHT22 nem+sıcaklık (60 TL) |
| **Alt toplam sensörler** | | **250–420 TL** | | |

---

## KATEGORİ 4: Mekanik ve Saha

| Malzeme | Amaç | Fiyat (TL) | Tedarikçi |
|---------|------|-----------|-----------|
| Su geçirmez kutu (IP65) | Node koruma | 80–150 | Elektrik malzeme satıcısı |
| Kablo rakoru (M12) | Kablo geçişi | 20–40 | Elektrikçi |
| Montaj direkleri / kazıklar | Saha kurulumu | 30–50 | Yapı marketi |
| **Alt toplam mekanik** | | **130–240 TL** | | |

---

## TOPLAM BÜTÇE

| Kategori | Min (TL) | Max (TL) |
|----------|---------|---------|
| MFC Bileşenleri | 680 | 1.110 |
| Elektronik | 785 | 1.350 |
| Sensörler | 250 | 420 |
| Mekanik / Saha | 130 | 240 |
| **TOPLAM** | **1.845** | **3.120** |

**BİLSEM Bütçe Notu:** Tuz köprüsü + karbon keçe + ESP32 WiFi kombinasyonuyla minimum ~1.845 TL'ye düşürülebilir. Okul elekronikleri (multimetre vb.) varsa daha da düşer.

---

## Tedarikçi Rehberi

| Tedarikçi | Web | Ne İçin |
|-----------|-----|---------|
| Robotistan | robotistan.com | Elektronik, sensörler, ESP32 |
| Direkt Drone | direktdrone.com | LoRa, drone elektronik |
| AliExpress | aliexpress.com | Ucuz sensörler (2–4 hafta kargo) |
| Mouser / Digi-Key | mouser.com | BQ25570 gibi özel IC (ithalat) |
| Yapı marketi | Bauhaus / Koçtaş | PVC, epoksi, mekanik |

---

## Bağlantılar
- [[sistem-mimarisi]] — Hangi malzeme hangi katmanda
- [[mfc-temelleri]] — MFC malzemeleri seçim kriterleri
- [[guvenlik]] — Kimyasal malzeme güvenliği
- [[proje-plani]] — Faz 0: malzeme temini
