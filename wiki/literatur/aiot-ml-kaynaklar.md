---
title: AIoT ve ML — Literatür
created: 2026-04-26
updated: 2026-04-26
tags: [literatür, aiot, ml, anomali, lora, iot, edge-ai]
level: proje
---

# AIoT ve Makine Öğrenmesi — Temel Kaynaklar

## Özet
Yapay zeka destekli IoT sensör ağları, anomali tespiti, LoRa protokolü ve kenar yapay zekası üzerine 12 açık erişimli akademik yayın.

---

## 1. Isolation Forest + Autoencoder — Yeşil IoT (2025) ⭐

**Yazar:** Jamshidi, S. vd.  
**Kaynak:** arXiv:2511.18235  
**PDF:** `pdf/isolation-forest-green-iot-2025.pdf`

**Ne Diyor:**
EcoDefender: Autoencoder + Isolation Forest hibrit anomali tespiti.
- %94 tespit doğruluğu
- Sadece %22 CPU kullanımı
- Autoencoder-only'ye göre %30 daha az enerji
- 27 ms çıkarım gecikmesi (gerçek zamanlı)

**Projeye Katkısı:** `ai/train.py`'deki Isolation Forest modelimizin doğrudan teorik karşılığı. Hibrit yaklaşım gelecekte eklenebilir.

---

## 2. Federe Isolation Forest — Kenar IoT (2025) ⭐

**Yazar:** Vasiljevic, P. vd.  
**Kaynak:** arXiv:2506.05138  
**PDF:** `pdf/federated-isolation-forest-2025.pdf`

**Ne Diyor:**
FLiForest: Kaynak kısıtlı IoT cihazlarında federe öğrenme ile Isolation Forest.
- %96 doğruluk (etiketsiz veriyle!)
- Bellek kullanımı < **160 KB** → ESP32 uyumlu!
- MicroPython ile çalışabilir

**Projeye Katkısı:** Isolation Forest modelimizin ESP32'de çalışabileceğinin kanıtı. 160 KB bellek → ESP32'nin 520 KB RAM'ine sığar.

---

## 3. SPARC-LoRa — Tarımsal İzleme (2024) ⭐

**Yazar:** Wang, X. vd.  
**Kaynak:** arXiv:2401.13569  
**PDF:** `pdf/sparc-lora-agriculture-2024.pdf`

**Ne Diyor:**
Ölçeklenebilir, düşük güçlü, bulut entegreli LoRa tarım sistemi.
- MCU + LoRa uyku modu → dramatik güç azalması
- Utah ve Nebraska'da gerçek saha testi
- Docker + açık kaynak altyapı

**Projeye Katkısı:** Sistemimizle neredeyse aynı mimari. Saha konuşlandırma protokolü için referans. `firmware/esp32_main.ino` tasarımını valide eder.

---

## 4. Markov Süreciyle WSN Anomali Tespiti (2025)

**Yazar:** Mishra, R. vd.  
**Kaynak:** arXiv:2511.00481  
**PDF:** `pdf/wsn-anomaly-ml-survey-2023.pdf`

**Ne Diyor:**
Sürekli sensör verisi → sonlu durumlar → Markov zinciri ile anomali tespiti.
- Etiketsiz veri ile çalışır
- Düşük hesaplama yükü
- **F1 = 0.86** Intel Berkeley Araştırma Lab verisinde

**Projeye Katkısı:** Isolation Forest alternatifi. Düşük bellekli MCU'lar için daha uygun olabilir.

---

## 5. AquaFusionNet — Kenar Su Kalitesi (2025)

**Yazar:** Kristanto, S.P. vd.  
**Kaynak:** arXiv:2512.06848  
**PDF:** `pdf/water-contamination-lstm-2025.pdf`

**Ne Diyor:**
Mikroskop görüntüsü + fizikokimyasal sensör füzyonu ile su kalitesi tespiti.
- %94.8 patojen tespit doğruluğu
- Sadece **4.8W** kenar donanımında
- 6 ay, 7 tesis, 1.84 milyon kare test

**Projeye Katkısı:** Su kalitesi + ML sistemimizin hedef performans çıtası. Sensör füzyonu yaklaşımını gelecekte uygulayabiliriz.

---

## 6. WSN Anomali Tespiti ML Araştırması (2023)

**Yazar:** Haque, A. vd.  
**Kaynak:** arXiv:2303.08823  
**PDF:** `pdf/wsn-anomaly-ml-survey-2023.pdf`

**Ne Diyor:**
Kapsamlı derleme: denetimli, denetimsiz, yarı-denetimli anomali tespiti.
- Denetimsiz yöntemler (Isolation Forest) etiketsiz IoT verisi için en iyi
- Yarı-denetimli yaklaşımlar eksik etiket durumunda köprü

**Projeye Katkısı:** Algoritma seçimi teorik kılavuzu. "Neden Isolation Forest?" sorusuna akademik cevap.

---

## 7. Su Kirliliği Tespiti — Kavram Kayması (2025)

**Yazar:** Li, J. vd.  
**Kaynak:** arXiv:2501.02107  
**PDF:** `pdf/water-contamination-lstm-2025.pdf`

**Ne Diyor:**
LSTM-VAE tabanlı gerçek zamanlı su kirlilik tespiti.
- Kavram kaymasını (sensör eskimesi, kalibrasyon) öğrenir
- Dağıtık tespit + lokalizasyon

**Projeye Katkısı:** Uzun vadeli sistem stabilitesi için kavram kayması önemli. pH ve nem sensörlerinde kalibrasyon kaymasını ele almak için referans.

---

## 8. Kenar AI — Model Sıkıştırma (2024)

**Yazar:** Francy, S., Singh, R.  
**Kaynak:** arXiv:2409.02134  
**PDF:** arXiv'den indirilebilir

**Ne Diyor:**
ESP32/MCU için sinir ağı sıkıştırması.
- Yapısal budama: %75 boyut azalması
- Dinamik kuantizasyon: %95 parametre azalması
- Birleşik: %89.7 boyut azalması, %92.5 doğruluk, **20 ms çıkarım**

**Projeye Katkısı:** ESP32'de TinyML çalıştırmak istiyorsak bu yolları uygulamalıyız. Faz 3 yazılım geliştirme için.

---

## 9. LoRaWAN Enerji Verimliliği — Pekiştirmeli Öğrenme (2023)

**Yazar:** Lin, K. vd.  
**Kaynak:** arXiv:2311.01743  
**PDF:** `pdf/lorawaan-energy-rl-2023.pdf`

**Ne Diyor:**
Yayılım faktörü (SF) ataması için RL (çift derin Q-ağı).
- SF seçimi → enerji verimliliğinde kritik etki
- Yeraltı ve uydu bağlantılı senaryolarda test edildi

**Projeye Katkısı:** `simulation/transmission_model.py`'deki SF7–SF12 analizimizin teorik derinleştirilmesi. Optimal SF otomatik seçilebilir.

---

## 10. MCU için Sinir Ağı Kuantizasyonu (2025)

**Yazar:** Abushahla, H.A. vd.  
**Kaynak:** arXiv:2508.15008  
**PDF:** arXiv'den indirilebilir

**Ne Diyor:**
TinyML kapsamlı araştırması. ARM Cortex-M ve RISC-V donanımları.
- 8-bit kuantizasyon standart
- NPU'lar kenar çıkarımını hızlandırıyor

**Projeye Katkısı:** Gelecekte karar modelini ESP32'ye taşıma rehberi.

---

## 11. LoRaWAN Çevrimiçi Kaynak Tahsisi (2025)

**Yazar:** Wang, R. vd.  
**Kaynak:** arXiv:2509.10493  
**PDF:** arXiv'den indirilebilir

**Ne Diyor:**
D-LoRa ve CD-LoRa dağıtık öğrenme çerçeveleri.
- Paket iletim oranı: %10.8 artış
- Enerji verimliliği: **%26.1 artış**

**Projeye Katkısı:** Birden fazla node olduğunda LoRa parametrelerini otomatik optimize etmek için.

---

## 12. Su Kalitesi ML — Çok Değişkenli Analiz (2025)

**Yazar:** Cardia, M. vd.  
**Kaynak:** arXiv:2512.02508  
**PDF:** arXiv'den indirilebilir

**Ne Diyor:**
UV-Vis spektroskopisi + ML ile su kalitesi tahmini.
SHAP analizi ile yorumlanabilir AI.

**Projeye Katkısı:** pH + iletkenlik + gaz sensörü füzyonu ile su kalitesi tahmininde SHAP yorumlanabilirliği eklenebilir.

---

## Özet Karşılaştırma Tablosu

| Konu | En İyi Paper | Bulgu |
|------|-------------|-------|
| Isolation Forest IoT | arXiv:2511.18235 | %94 doğruluk, 27ms |
| LoRa tarım | arXiv:2401.13569 | Gerçek saha testi |
| WSN Anomali | arXiv:2511.00481 | F1=0.86 etiketsiz |
| Edge AI bellek | arXiv:2506.05138 | <160KB ESP32 uyumlu |
| LoRa enerji | arXiv:2311.01743 | SF seçimi kritik |

---

## Bağlantılar
- [[../sistem-mimarisi]] — AI katmanı
- [[mfc-enerji-kaynaklar]] — MFC literatürü
- [[index]] — Tüm literatür dizini
