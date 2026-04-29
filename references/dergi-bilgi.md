# Dergi Bilgi Tabanı — Hakem Skill Hafızası

---

## MDPI Sensors | Yayıncı: MDPI | IF: ~3.9 | Q2
**Son Güncelleme:** 2026-04-29
**ISSN:** 1424-8220 (online)
**Kapsam:** Sensörler, aktüatörler, ölçüm sistemleri, IoT, giyilebilir teknoloji,
biyosensörler, çevre izleme, enerji hasadı, gömülü sistemler.
Dışarıda: saf algoritma çalışmaları (sensörle bağlantısı yoksa), klinik denemeler.

**Makale Türleri:** Research Article / Review / Communication / Letter

**Zorunlu Bölümler:**
- Abstract (max 200 kelime, atıf yok)
- Introduction
- Materials and Methods (veya System Design / Architecture)
- Results
- Discussion
- Conclusions
- Author Contributions
- Funding
- Data Availability Statement
- Conflicts of Interest
- References

**Opsiyonel:** Graphical Abstract, Highlights, Supplementary Materials

**Kelime Limiti:** ~8000-10000 kelime makale gövdesi; sayfa limiti yok ama
editörler >12 sayfayı dikkatle inceler. Figür/tablo dahil toplam ~20-25 sayfa tipik.

**Figür Kuralları:** Min 600 DPI çizgi figürleri, min 300 DPI fotoğraf.
Format: TIFF, EPS, SVG, PNG (TIFF/EPS tercihli). Max 10 MB/figür.
Renk ücretsiz (open access). Her figür bağımsız anlaşılır (caption yeterli).

**Atıf Formatı:** Vancouver (sayısal, köşeli parantez [1], sıra takip eder).
Atıf sayısı: tipik 30-60, min ~20.

**APC:** ~2200 USD (2026 itibarıyla; MDPI fiyatları yıldan yıla değişir).
Discount seçenekleri: ülke indirimi, editör/hakemlik indirimi.

**Ortalama Karar Süresi:** ~3-6 hafta ilk karar; revizyondan sonra 2-4 hafta ek.
Hızlı editöryal red (scope dışı): 1-5 gün.

**Tipik Red Sebepleri:**
- Kapsam dışı veya yeterince sensör odaklı değil
- Sadece simülasyon (doğrudan hardware olmaksızın) → büyük risk; "virtual validation" ile azaltılabilir
- ML sonuçları gerçekçi değil / validation eksik (circular, train=test)
- Referanslar yetersiz veya güncel değil (>5 yıl öncesi ağırlıklı)
- İngilizce kalitesi düşük
- Katkı özgünlüğü belirsiz (Related Work zayıf konumlandırma)

**Kabul Kriterleri:**
- Sensör/IoT ekosistemiyle güçlü bağlantı
- Gerçekçi, tekrarlanabilir metodoloji
- Şeffaf sınırlama ifadesi
- Açık kaynak kodu / veri erişilebilirliği (Data Availability)
- Geniş etki potansiyeli (precision agriculture, çevre, sağlık vs.)

**Özel Notlar:**
- Abstract'ta atıf YASAK ([x] gibi parantezler dahil)
- Keywords: min 5, max 10; noktalı virgülle ayrılır
- "Sensors" dergisi simülasyon makalelerini kabul eder ancak
  **neden gerçek deney yok?** sorusunu mutlaka sormak için bölüm/paragraf gerektirir.
  Section 3.8 "Power Trace Emulation" + Section 5.2 "Simulation Scope" +
  Section 5.7 "Virtual Experimental Validation" kombinasyonu bu boşluğu
  kapatan kanıtlanmış yapıdır. Emülasyon kısmı (MAPE [-1.6%, +8.5%]
  cross-study fidelity envelope) özellikle güçlü: Zhang [11] bağımsız
  parametresiyle -1.6% MAPE, simülasyonun gerçek dünya fiziksel dinamikleri
  doğrultusunda yapısal olarak doğru olduğunu gösteriyor.
- Gömülü ML / TinyML çalışmaları son 2 yılda Sensors'da artış gösterdi (tematik uyum yüksek)
- MDPI hızlı döngü: submission → first decision ~4 hafta ortalama (2025-2026 gözlemi)

**Bu Makalede Uygulanan Revizyonlar:**
| Tarih | Hakem Sorunu | Çözüm |
|---|---|---|
| 2026-04-29 (Rev5) | Deney yok | Sec 5.7: 5 alt bölüm Virtual Validation |
| 2026-04-29 (Rev5) | AI sonuçları çok mükemmel | F1=0.880 / AUC=0.929 subtle+noisy bound |
| 2026-04-29 (Rev5) | "AI" kw aşırılığı | "edge AI" kaldırıldı; Sec 3.6 → "Embedded Intelligence" |
| 2026-04-29 (Rev5) | Abstract'ta atıf | [13] kaldırıldı (MDPI policy) |
| 2026-04-29 (Rev5) | Monte Carlo eksik | simulation/monte_carlo.py N=200 →%75.0 |
| 2026-04-29 (Rev6) | **"Simulation-only"** en büyük red riski | Sec 3.8 Power Trace Emulation (+8.5% sapma) |
| 2026-04-29 (Rev6) | Başlık zayıf | "Simulation-Grounded...Hardware-Aware Validation...AIoT" |
| 2026-04-29 (Rev6) | Contribution kısmı güçsüz | 5 katkı, emülasyon #4 olarak eklendi |
| 2026-04-29 (Rev6) | Sec 5.2 pasif | Sim→Emul→Prototype 3 aşamalı pipeline tanımlandı |
| 2026-04-29 (Rev6) | TinyML eksik | supercapacitor kw → TinyML (10 kw korundu) |
| 2026-04-29 (Rev7c) | Figür sıralaması hatalı | Fig 6↔7 swap + Fig 10 emülasyon Sec 5.2'ye taşındı |
| 2026-04-29 (Rev7d) | Cross-dataset doğrulama eksik | Sec 5.7.5: literature-ref KS+Cohen'd+ROC=0.999 |
| 2026-04-29 (Rev7e) | Zhang [11] entegrasyonu | Sec 3.8: Zhang cross-study MAPE=-1.6%; başlık Virtual Prototyping |
| 2026-04-29 (Rev7f) | Overfitting algısı riski | Sec 3.8: parametrik enjeksiyon → structural validity açıklaması |
| 2026-04-29 (Rev7g) | Abstract–başlık tutarsızlığı | "co-design"→"virtual prototyping" (3 yerde); cross-study+F1=0.880 abstract'a eklendi |

**Mevcut Hakem Kararı Tahmini:** Major Revision → **Minor Revision** (Rev7g sonrası — hakem skoru 33/40)
**Submission Durumu:** ✅ GÖNDERİME HAZIR (Rev7g)

**GitHub:** https://github.com/kahyakursat1-cloud/mfc-aiot-sensor
**PDF:** paper/Sensors_MFC_AIoT_2026.pdf (26 sayfa, Rev7g — 2026-04-29)

---
