# TASKS — Mikrobiyal AIoT Sensör Ağı

Son güncelleme: 2026-04-26

---

## Faz 0: Simülasyon ve Modelleme  ← ÖNCE BURASI
- [ ] `python main.py` çalıştır, grafikleri incele
- [ ] `simulation/energy_model.py` ile bütçe analizi yap — hangi döngü süresi çalışıyor?
- [ ] `simulation/transmission_model.py` — SF7 mi SF9 mu daha iyi?
- [ ] `simulation/mfc_simulation.py` ile 48 saat simüle et — TX başarı oranı ≥ %85 mi?
- [ ] `ai/train.py` çalıştır — anomali modeli F1 ≥ 0.85 mi?
- [ ] `ai/decision_model.py` — 5 farklı enerji seviyesinde kararları test et
- [ ] Simülasyon sonuçlarına göre enerji bütçesini kilitle → `wiki/sistem-mimarisi.md` güncelle

## Faz 1: MFC Prototip Yapımı
- [ ] Anot/katot elektrot malzemelerini temin et (grafit kumaş, paslanmaz çelik)
- [ ] MFC odası için PVC/akrilik kap tasarımı ve yapımı
- [ ] PEM membran kurulumu (Nafion 117 veya ev yapımı tuz köprüsü alternatifi)
- [ ] İlk bakteri aşılama (çamur/biyofilm kaynağı bul)
- [ ] MFC voltaj çıkışı ölçümü ve kayıt (hedef: >0.3V açık devre)

## Faz 2: Sensör Node Montajı
- [ ] ESP32 geliştirme kartı temin ve test
- [ ] Toprak nemi sensörü bağlantısı ve kalibrasyon
- [ ] DS18B20 sıcaklık sensörü entegrasyon
- [ ] pH sensörü (analog) bağlantı ve kalibrasyon
- [ ] MFC → güç yönetimi devresi → ESP32 bağlantısı
- [ ] Süper kapasitör tampon devre testi

## Faz 3: Yazılım Geliştirme
- [ ] ESP32 Arduino firmware (sensör okuma + LoRa gönderim)
- [ ] LoRa gateway kurulumu ve bağlantı testi
- [ ] Veri loglama altyapısı (MQTT veya CSV)
- [ ] Python ML modeli (anomali tespiti — Isolation Forest)
- [ ] Dashboard arayüzü (Grafana veya basit web)
- [ ] Enerji yönetimi algoritması (deep sleep + wake cycle)

## Faz 4: Saha Testi ve Kalibrasyon
- [ ] İç mekan test konuşlandırması (kontrollü ortam)
- [ ] MFC performans ölçümü (gerçek yük altında)
- [ ] Sensör doğruluk validasyonu (referans cihazla karşılaştırma)
- [ ] ML model eğitimi (toplanan gerçek verilerle)
- [ ] 48 saatlik kesintisiz çalışma testi
- [ ] Güç bütçesi analizi (üretilen vs. tüketilen)

## Faz 5: Raporlama ve Sunum
- [ ] Teknik rapor taslağı
- [ ] Ölçüm verileri grafikleri
- [ ] Sistem blok diyagramı güncelle
- [ ] Proje sunusu hazırla (BİLSEM/yarışma formatı)
- [ ] Maliyet analizi güncelle (gerçek harcamalar)

---

## Tamamlananlar
- [x] Proje wiki yapısı oluşturuldu (2026-04-25)
- [x] CLAUDE.md ve TASKS.md hazırlandı (2026-04-25)
- [x] Temel wiki sayfaları yazıldı: proje-plani, sistem-mimarisi, malzeme-listesi, mfc-temelleri, guvenlik (2026-04-25)
- [x] simulation/ klasörü: 5 Python modülü (2026-04-26)
- [x] ai/ klasörü: decision_model.py + train.py (2026-04-26)
- [x] firmware/ klasörü: esp32_main.ino + lora_driver (2026-04-26)
- [x] main.py uçtan uca simülasyon giriş noktası (2026-04-26)

---

## Engeller / Açık Sorular
- MFC için hangi bakteri kaynağı kullanılacak? (çamur, atık su, toprak)
- LoRa mı WiFi mesh mi? (kapsama alanına göre karar)
- Öğrenci sayısı ve rol dağılımı netleştirilmeli
