---
title: Sistem Mimarisi — Mikrobiyal AIoT Sensör Ağı
created: 2026-04-25
updated: 2026-04-25
tags: [mimari, aiot, iot, esp32, lora, ml, sistem]
level: proje
---

# Sistem Mimarisi

## Özet
Sistem 4 katmandan oluşur: (1) Enerji üretimi (MFC), (2) Güç yönetimi ve sensör node (ESP32), (3) Veri iletimi (LoRa/WiFi), (4) Merkezi analiz ve yapay zeka (ML anomali tespiti). Tüm sistem dış güç kaynağı olmadan çalışır.

---

## Blok Diyagram

```
┌─────────────────────────────────────────────────────────────┐
│                    KATMAN 1: ENERJİ                          │
│                                                             │
│   [Toprak/Su/Çamur]                                         │
│         │                                                    │
│   [Bakteri Biyofilmi]  ←── Organik madde tüketimi           │
│         │                                                    │
│   [Anot] ── e⁻ ──> [Katot]   (0.3–0.8 V / hücre)           │
│         │                                                    │
│   [MFC Hücre Dizisi]  →  0.3–3.3V (N hücre seri)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  KATMAN 2: GÜÇ YÖNETİMİ                     │
│                                                             │
│   [LTC3108 / BQ25570]  ←── Enerji hasat IC                  │
│         │                                                    │
│   [Süper Kapasitör]  ←── Tampon (1–10F, 2.7V)               │
│         │                                                    │
│   [3.3V LDO Regülatör]  →  ESP32'ye sabit güç               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               KATMAN 3: ALGILAMA (SENSOR NODE)              │
│                                                             │
│   ESP32 (Deep Sleep: ~10µA, Aktif: ~80mA)                   │
│      │                                                       │
│      ├── Toprak Nemi Sensörü (kapasitif, analog)             │
│      ├── DS18B20 Sıcaklık (dijital, 1-Wire)                 │
│      ├── pH Sensörü (analog, 0–14)                           │
│      └── MQ-135 Hava Kalitesi (CO₂/NH₃, analog)            │
│                                                             │
│   Uyku döngüsü: 10 dk uyu → 5 sn ölç → gönder → uyu        │
└──────────────────────────┬──────────────────────────────────┘
                           │ LoRa 433/868 MHz
                           │ (≤2km mesafe, 50mW TX)
┌──────────────────────────▼──────────────────────────────────┐
│               KATMAN 4: MERKEZİ ANALİZ                      │
│                                                             │
│   [LoRa Gateway / Raspberry Pi]                             │
│         │                                                    │
│   [MQTT Broker]  →  Veri tamponu                            │
│         │                                                    │
│   [ML Modeli: Isolation Forest]                             │
│      ├── Anomali tespiti (pH ani düşüşü, sıcaklık spike)    │
│      └── Trend analizi (nem kuraklık öngörüsü)              │
│         │                                                    │
│   [Dashboard]  →  Grafana / basit web arayüzü               │
└─────────────────────────────────────────────────────────────┘
```

---

## Katman Sorumlulukları

### Katman 1 — Enerji Üretimi (MFC)
- Bakteri biyofilmi organik maddeyi oksitler → elektron üretir
- Anot: elektron alıcı (grafit kumaş)
- Katot: elektron vericiye oksijen indirger (hava katot tercih)
- Çıkış: 0.3–0.8V, 0.1–5 mA (hücre boyutu ve bakteri yoğunluğuna bağlı)

### Katman 2 — Güç Yönetimi
- Hasat IC (BQ25570): MFC'nin düşük, dalgalı voltajını güvenli şarj döngüsüne çevirir
- Süper kapasitör: ölçüm/iletim anlık güç talebini karşılar
- LDO: ESP32'ye kararlı 3.3V sağlar

### Katman 3 — Sensör Node
- ESP32 deep-sleep ile enerji bütçesi yönetir
- Her ölçüm döngüsü: uyu (10 dk) → uyan → ölç (2–5 sn) → LoRa gönder → uyu
- Ortalama tüketim hedef: < 1 mA

### Katman 4 — Merkezi Analiz
- Gateway sabit güç kaynağı (okul/bina elektriği) ile çalışabilir
- ML anomali tespiti: normal baseline'dan sapmaları bulur
- İnsan uyarısı: eşik aşıldığında bildirim (SMS, e-posta, dashboard alarm)

---

## 3 Seviye Bakış

### 🟢 BYF
Sistem bir "biyolojik pil" gibi çalışır. Bakteriler yemek yerken elektrik üretir, bu elektrik sensörlere gider, sensörler çevreyi ölçer.

### 🟡 ÖYG
MFC → DC-DC converter → kapasitör tamponu → ESP32 besleme. ESP32 her 10 dakikada uyanır, sensör okur, LoRa ile gönderir, uyur. Güç bütçesi: üretim ≥ tüketim olmalı.

### 🔴 PROJE
Güç bütçesi dengesi: P_üretim = V_mfc × I_mfc (ortalama) ≥ P_tüketim = (I_aktif × t_aktif + I_uyku × t_uyku) / T_döngü. MFC empedans eşleme, maksimum güç transferi noktası (MPP tracking) ile optimize edilir.

---

## Bağlantılar
- [[mfc-temelleri]] — Katman 1 fiziksel temeli
- [[malzeme-listesi]] — Her katmanın bileşen listesi
- [[proje-plani]] — Hangi fazda hangi katman kurulur
- [[guvenlik]] — 🚨 Özellikle kimyasal güvenlik
