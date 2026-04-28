---
title: MFC Enerji Hasadı — Literatür
created: 2026-04-26
updated: 2026-04-26
tags: [literatür, mfc, enerji-hasadı, biyoelektrokimya, sensor]
level: proje
---

# MFC Enerji Hasadı — Temel Kaynaklar

## Özet
Mikrobiyal Yakıt Hücresi (MFC) tabanlı enerji hasadı ve çevre izleme üzerine 12 açık erişimli akademik yayın. Tümü PMC veya arXiv'den ücretsiz indirilebilir.

---

## 1. ML ile SMFC Güç Tahmini (2024) ⭐ En Önemli

**Yazar:** Hess-Dunlop, A., Kakani, H., Josephson, C.  
**Kaynak:** arXiv:2406.16939  
**PDF:** `pdf/lstm-smfc-prediction-2024.pdf`

**Ne Diyor:**
Toprak MFC'sinin (SMFC) değişken güç üretimini LSTM sinir ağıyla tahmin ediyor.
- %2.33–5.71 ortalama mutlak yüzde hata
- 3 dakikadan 1 saate kadar öngörü ufku
- Cihaz çalışma süresini %100 artıran çizelgeleme

**Projeye Katkısı:** Simülasyon modelimizin validasyonu için referans. MFC güç çıkışı ML ile tahmin edilebilir → akıllı uyku döngüsü mümkün.

---

## 2. Biyohücreden Enerji Hasadı (2018)

**Yazar:** Catacuzzeno, L. vd.  
**Kaynak:** arXiv:1808.07000  
**PDF:** `pdf/biocell-energy-harvesting-2018.pdf`

**Ne Diyor:**
Xenopus oosit hücrelerinin membran potansiyelinden elektrik enerjisi toplandı.
Toplanan enerji kondansatörde biriktirildi, RF sinyali olarak iletildi.

**Projeye Katkısı:** MFC'nin fiziksel temelini kanıtlayan çalışma. Biyolojik → elektriksel dönüşüm mümkün ve kablosuz iletimde kullanılabilir.

---

## 3. MFC Sürdürülebilir Elektrik Üretimi — Genel Bakış (2023)

**Yazar:** Apollon, W.  
**Kaynak:** Membranes, 13(11), 884. DOI: 10.3390/membranes13110884  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10672772/

**Ne Diyor:**
MFC'nin farklı konfigürasyonları, güç yoğunlukları ve ölçeklendirme sorunlarını kapsamlı biçimde inceleyen derleme.
- Maksimum güç yoğunluğu: **2203 mW/m²**
- Coulombik verimlilik: %55.6'ya kadar
- KOİ giderimi: %93.7

**Projeye Katkısı:** Tasarım kıstasları için referans tablo. Elektrot malzemesi seçimine rehberlik eder.

---

## 4. MFC Tabanlı Organik Madde Sensörleri (2023)

**Yazar:** Yao, H., Xiao, J., Tang, X.  
**Kaynak:** Bioengineering, 10(8), 886. DOI: 10.3390/bioengineering10080886  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10451650/

**Ne Diyor:**
MFC'nin hem enerji kaynağı hem de biyosensör olarak çalışabileceğini gösteriyor.
BOD/KOİ tespiti, su kalitesi izleme, farklı tasarım varyasyonları.

**Projeye Katkısı:** Sistemimizde MFC = güç + sensör çift işlevi mümkün. Su kalitesi ile korelasyon kurulabilir.

---

## 5. SMFC Elektrot Yüzey Alanı Optimizasyonu (2018)

**Yazar:** Yang, Y. vd.  
**Kaynak:** RSC Advances, 8, 24657. DOI: 10.1039/c8ra05069d  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9082551/

**Ne Diyor:**
Anot/katot yüzey alan oranının optimizasyonu: **1:1.33 oranı en iyi güç**.
Yanlış oran → seri bağlı hücrelerde voltaj terselmesi.

**Projeye Katkısı:** MFC tasarım parametresi. Seri bağlama yaparken bu oranı koru.

---

## 6. MFC ile Sıcaklık/Nem Sensörü (2015) ⭐ Projeye En Yakın

**Yazar:** Zheng, Q. vd.  
**Kaynak:** Sensors, 15(9), 23126. DOI: 10.3390/s150923126  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4610421/

**Ne Diyor:**
Tek bir MFC → süper kapasitör + şarj pompası → DC-DC dönüştürücü → kablosuz sensör (nRF24L01).
- Enerji verimliliği: %15.7–16.7
- Başarıyla sıcaklık ve nem ölçümü + iletim

**Projeye Katkısı:** Sistemimizin doğrudan kanıtı. Güç yönetimi devresi tasarımımız bu çalışmaya dayanıyor.

---

## 7. Süper Kapasitif MFC (2016)

**Yazar:** Houghton, J. vd.  
**Kaynak:** Bioresource Technology, 218, 552. DOI: 10.1016/j.biortech.2016.06.105  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5001197/

**Ne Diyor:**
Katot alanını ×2 yapmak → tepe güç %120 artış, iç direnç %47 azalış.
21 cm³ kompakt cihaz → ~25 mW tepe güç.

**Projeye Katkısı:** Kompakt MFC tasarımı mümkün. Katot geometrisi kritik performans faktörü.

---

## 8. Öz Tabakalı Süper Kapasitif MFC (2019)

**Yazar:** Santoro, C. vd.  
**Kaynak:** Electrochimica Acta, 305, 254. DOI: 10.1016/j.electacta.2019.03.194  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6559283/

**Ne Diyor:**
0.55 mL hacimli mini MFC + entegre süper kapasitör.
- Tepe güç: 1.20 ± 0.04 mW  
- 44 saatte ~2600 şarj/deşarj döngüsü
- ESR sadece %10 arttı

**Projeye Katkısı:** Uzun ömürlülük verisi. 44 saat stabillik = proje hedefimizle uyumlu.

---

## 9. MFC Son Gelişmeler ve Uygulamalar (2025)

**Yazar:** Chakma, R. vd.  
**Kaynak:** Global Challenges. DOI: 10.1002/gch2.202500004  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC12065106/

**Ne Diyor:**
2025 yılı kapsamlı derlemesi. Robotik, biyosensör, atık su arıtımı, biyohidrojen.
- Güç yoğunluğu: 2.44–3.31 W/m²
- Önemli bariyerler: düşük güç, yavaş başlangıç, maliyet

**Projeye Katkısı:** Güncel benchmark değerleri. Ticari bariyerleri anlayıp alternatif tasarım geliştirmek için.

---

## 10. MFC Kapsamlı Materyal ve Yapı İncelemesi (2024)

**Yazar:** Jalili, P. vd.  
**Kaynak:** Heliyon, 10(3), e25439. DOI: 10.1016/j.heliyon.2024.e25439  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10873675/

**Ne Diyor:**
Membran'lı vs. membransız MFC karşılaştırması. Biyofilm, iç direnç, substrat kaybı faktörleri.

**Projeye Katkısı:** Tuz köprüsü alternatifi için teorik dayanak. Membransız tasarımın avantaj/dezavantajları.

---

## 11. Karasal MFC ile WSN Beslemesi (2016) ⭐ Projeye En Yakın

**Yazar:** Zhang, D. vd.  
**Kaynak:** Int. J. Mol. Sci., 17(5), 762. DOI: 10.3390/ijms17050762  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4855932/

**Ne Diyor:**
Toprak bazlı MFC ile kablosuz sensör ağı beslendi. Toprak nemi ve sıcaklık değişkenlerinin MFC performansına etkisi ölçüldü.

**Projeye Katkısı:** Sistemimizin tam karşılığı. Toprak koşullarının MFC verimine etkisini anlayıp kalibrasyon yapmak için.

---

## 12. Kağıt Tabanlı Taşınabilir MFC Sensörü (2019)

**Yazar:** Cho, J.H. vd.  
**Kaynak:** Sensors, 19(24), 5452. DOI: 10.3390/s19245452  
**Erişim:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6960574/

**Ne Diyor:**
Tek kullanımlık kağıt MFC biyosensörü. Formaldehit konsantrasyonu ile voltaj düşüşü arasında R²=0.931 doğrusal ilişki.

**Projeye Katkısı:** Düşük maliyetli sensör alternatifleri için ilham. Gaz sensörünü MFC ile entegre etmek mümkün mü?

---

## Bağlantılar
- [[../mfc-temelleri]] — Kavram sayfası
- [[../malzeme-listesi]] — Elektrot malzeme seçimi
- [[aiot-ml-kaynaklar]] — AIoT literatürü
- [[index]] — Tüm literatür dizini
