---
title: Güvenlik Rehberi — Mikrobiyal AIoT
created: 2026-04-25
updated: 2026-04-25
tags: [güvenlik, mfc, kimyasal, elektrik, biyogüvenlik]
source: —
level: tümü
---

# 🚨 GÜVENLİK — MFC ve AIoT Sensör Ağı

## Özet
Bu proje bakteri kültürü, kimyasal çözeltiler ve düşük gerilimli elektrik içerir. Çoğu tehlike düşük riskte olmakla birlikte, doğru KKE ve prosedürler uygulanmazsa enfeksiyon, kimyasal tahriş veya kısa devre riski vardır.

---

## KİŞİSEL KORUYUCU EKİPMAN (KKE)

| Aktivite | Gerekli KKE |
|----------|-------------|
| Bakteri aşılama / örnekleme | Lateks/nitril eldiven + gözlük |
| Kimyasal çözelti hazırlama | Nitril eldiven + gözlük + önlük |
| Lehimleme / devre montajı | Duman filtresi / havalandırma |
| Saha örnekleme (toprak/su) | Nitril eldiven |
| Batarya / kondansatör şarjı | Yangın söndürücü yakın olsun |

---

## 1. Biyolojik Güvenlik

### Bakteri Kültürü
- Geobacter / Shewanella gibi elektroji-aktif bakteriler **Biyogüvenlik Seviye 1** — düşük risk
- Atık su / çamur kaynaklı karışık kültür: eldivenle çalış, mukoza teması yok
- Örnekleme sonrası el yıkama zorunlu
- Kullanılan malzemeleri %10 çamaşır suyu ile dezenfekte et

### Bertaraf
- Bakteri kültürü içeren sıvıyı kanalizasyona dökmeden önce kaynat veya çamaşır suyu ekle
- Elektrotları normal çöpe at (ağır metal içermiyorsa)
- PEM membran: kimyasal atık olarak ayır

---

## 2. Kimyasal Güvenlik

### MFC'de Kullanılan Kimyasallar

| Kimyasal | Risk | Önlem |
|----------|------|-------|
| Sodyum asetat (substrat) | Düşük | Temasda yıka |
| Fosfat tampon çözeltisi | Düşük | Gözlük önerilir |
| Nafion çözeltisi (membran) | Orta — solvent içerir | Havalandırmalı ortamda, eldiven |
| Sülfürik asit (pH ayar) | Yüksek | Tam KKE, ASLA suya asit değil, asite su ekle |
| HCl (elektrot temizleme) | Orta-Yüksek | Çeker ocak veya dışarıda |

### Döküntü Prosedürü
1. Küçük döküntü: kağıt havluyla sil, çamaşır suyu ile nötralize et
2. Büyük döküntü: öğretmene haber ver, bölgeyi tahliye et

---

## 3. Elektrik Güvenliği

### MFC Gerilimleri
- Tek hücre çıkışı: 0.3–0.8V (tehlikesiz)
- Hücre dizisi (10 hücre): 3–8V (düşük risk)
- Süper kapasitör şarjlı: 2.7–5V (kısa devre ısı üretir — dikkat)

### Elektronik Montaj
- Devre kurulu iken **pili bağlama** — önce devreyi kur, sonra güç ver
- Lehimleme: duman solunum riski → pencereyi aç veya fan kullan
- LiPo batarya kullanılıyorsa: → **[[../../wiki/yapim/LiPo_Batarya_Guvenlik|LiPo Güvenlik Rehberi]]** oku
- Kısa devre testi için multimetre kullan, el değil

---

## 4. Saha Güvenliği

- Toprak / su örnekleme: eldiven giy, içme / yeme yok
- Dışarıda çalışırken hava durumuna dikkat (yağmur → elektronik kapla)
- Saha deneyi için öğretmen refakatı gerekli
- GPS konumunu not al (node geri toplanabilsin)

---

## Acil Durum

| Durum | Eylem |
|-------|-------|
| Kimyasal göz teması | 15 dk akan su, ambulans ara |
| Deri tahrişi | Sabun + su, devam ederse doktor |
| Elektrik çarpması (düşük gerilim) | Güç kes, durum değerlendirmesi |
| Yangın (batarya) | Kum veya CO₂ söndürücü, LiPo suyla söndürme |

---

## Bağlantılar
- [[proje-plani]] — hangi fazda hangi kimyasallar kullanılır
- [[malzeme-listesi]] — güvenli malzeme alternatifleri
- [[mfc-temelleri]] — MFC'nin nasıl çalıştığını anlamak için
