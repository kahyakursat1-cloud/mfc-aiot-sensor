---
title: Mikrobiyal Yakıt Hücresi (MFC) Temelleri
created: 2026-04-25
updated: 2026-04-25
tags: [mfc, biyoelektrokimya, enerji, bakteri, kavram]
level: tümü
---

# Mikrobiyal Yakıt Hücresi (MFC)

## Özet
MFC, bakterilerin organik maddeyi parçalarken serbest bıraktığı elektronları elektrik akımına dönüştüren bir biyokimyasal cihazdır. Pil gibi çalışır ama "yakıtı" çamur, atık su veya topraktaki organik maddedir — bitmez, yenilenir.

---

## 🟢 BYF — Günlük Hayat Analojisi

Bir limon pili deneyi yaptın mı? Limonun asidi iki farklı metal arasında elektron geçişini sağlar. MFC'de limon yerine bakteri var: bakteriler "yemeklerini" (organik madde) yerken elektronları serbest bırakır. Bu elektronları bir tel üzerinden toplarsak — elektrik olur!

**Basit deney fikri:** Çamur dolu bir kap + 2 grafit kalem ucu + LED = çalışan MFC!

---

## 🟡 ÖYG — Temel Prensipler ve Formüller

### Nasıl Çalışır?

```
ANOT ODASI (oksijensiz)          |  KATOT ODASI (oksijensiz)
                                  |
Organik madde + Bakteri          |  O₂ + 4H⁺ + 4e⁻ → 2H₂O
→ CO₂ + H⁺ + e⁻                  |
                                  |
   Elektron → tele → dış devre → katota
   Proton → membran üzerinden → katoda
```

- **Anot:** Bakteri elektronu bırakır → elektron akışı başlar
- **Katot:** Elektron + proton + oksijen → su oluşur (indirgenme)
- **Membran (PEM):** Sadece proton geçirir, elektronları engeller → dış devreye yönlendirir

### Temel Parametreler

| Parametre | Tipik Değer | Açıklama |
|-----------|-------------|----------|
| Açık devre voltajı (OCV) | 0.5–0.8 V | Yük bağlıyken düşer |
| Kısa devre akımı | 0.1–10 mA | Elektrot yüzeyine bağlı |
| Güç yoğunluğu | 10–500 mW/m² | Tasarıma çok bağımlı |
| İç direnç | 50–1000 Ω | Düşürülmesi hedef |

### Yapım Bileşenleri
1. **Anot:** Grafit kumaş / karbon keçe (bakteri biyofilmi için geniş yüzey)
2. **Katot:** Grafit + Pt katalizör (veya MnO₂ ucuz alternatif)
3. **Membran:** Nafion 117 (ideal) veya tuz köprüsü (ucuz)
4. **Substrat:** Sodyum asetat çözeltisi (kolay) veya atık su / çamur

---

## 🔴 PROJE — Mühendislik Detayları ve Optimizasyon

### Güç Çıkışını Artırma

**Elektrokimyasal engeller:**
- **Aktivasyon kaybı:** Elektrot yüzeyindeki reaksiyon başlatma enerjisi → Pt katalizör ile azaltılır
- **Ohmic kayıp:** İç direnç → Membran kalınlığı azalt, elektrot-membran mesafesini kıs
- **Konsantrasyon kaybı:** Yüksek akımda substrat bitişi → Substrat yenileme döngüsü

**Maksimum Güç Transferi:**
```
P_max = V_OCV² / (4 × R_internal)
```
Dış yük = İç direnç olduğunda maksimum güç aktarımı.

**Biyofilm Optimizasyonu:**
- Geobacter sulfurreducens: en yüksek elektron transfer verimliliği
- Shewanella oneidensis: mediyatör kullanır, daha kolay kültür
- Karışık kültür (çamur): kolay başlangıç, düşük ama stabil güç

### Seri/Paralel Bağlama
- Seri: Voltaj toplar (N hücre × 0.5V → 5V yeterli)
- Paralel: Akım toplar (güç bütçesi için tercih)
- Tek hücre güç yetmiyorsa: 6–10 hücre seri → 3–5V → BQ25570 ile ESP32 besleme

### Performans İyileştirme Stratejileri
1. Elektrot yüzey alanını artır (3D grafit yapılar, nanomateryal kaplama)
2. Substrat konsantrasyonunu optimize et (1–2 g/L sodyum asetat)
3. Sıcaklık kontrolü: 30–35°C bakteri aktivitesi için optimal
4. pH tamponu: 6.5–7.5 arası tut

---

## Türkiye'de Kaynaklar
- Grafit kalem uçları: kırtasiyeden (prototip için yeterli)
- Karbon keçe: elektronik/kaynak malzeme mağazaları
- Nafion 117: ithalat gerekebilir — tuz köprüsü alternatif kullan
- Sodyum asetat: kimyasal satıcılar veya gıda katkı maddesi olarak eczane

---

## Bağlantılar
- [[sistem-mimarisi]] — MFC'nin sistemdeki yeri (Katman 1)
- [[malzeme-listesi]] — Elektrot ve membran seçenekleri, fiyatlar
- [[guvenlik]] — 🚨 Kimyasal ve biyolojik güvenlik önlemleri
