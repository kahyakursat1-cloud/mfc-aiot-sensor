/*
 * esp32_main.ino — Mikrobiyal AIoT Sensör Node
 * ═══════════════════════════════════════════════
 * Akış (her uyanmada):
 *   Uyan → Sensörleri oku → Enerji kontrolü →
 *   Anomali tespiti → Karar ver → [Gönder] → Deep sleep
 *
 * Donanım:
 *   ESP32 DevKit v1
 *   Ra-02 LoRa 433 MHz (SX1278)
 *   DS18B20 sıcaklık (1-Wire)
 *   Kapasitif toprak nemi (analog)
 *   pH modülü (analog)
 *   MQ-135 gaz sensörü (analog)
 *   Süper kapasitör (1F 2.7V) + voltaj bölücü
 *
 * Kütüphaneler (Arduino Library Manager):
 *   - LoRa         (Sandeep Mistry)
 *   - OneWire      (Jim Studt)
 *   - DallasTemperature (Miles Burton)
 */

#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "lora_driver.h"

// ── Pin Tanımları ────────────────────────────────────────────────────────────
#define PIN_SOIL_MOISTURE  34   // ADC1 — kapasitif toprak nemi
#define PIN_PH             35   // ADC1 — pH modülü
#define PIN_GAS            32   // ADC1 — MQ-135
#define PIN_TEMP_DATA       4   // DS18B20 one-wire veri hattı
#define PIN_CAP_SENSE      33   // ADC1 — kapasitör voltaj bölücü (R1=R2=100kΩ)

#define PIN_LORA_SS         5
#define PIN_LORA_RST       14
#define PIN_LORA_DIO0       2

// ── Enerji Eşikleri (Volt) ───────────────────────────────────────────────────
#define CAP_FULL_V         2.70f
#define CAP_TX_MIN_V       1.80f    // Normal TX için minimum
#define CAP_EMRG_V         1.55f    // Acil (anomali) TX için minimum
#define CAP_DIVIDER        2.0f     // Voltaj bölücü oranı

// ── Uyu / Uyan Döngüsü ───────────────────────────────────────────────────────
#define SLEEP_US           (10ULL * 60 * 1000000)   // 10 dakika
#define FORCE_TX_WAKES     6                        // ~1 saatte bir zorla gönder

// ── Anomali Eşikleri ─────────────────────────────────────────────────────────
#define SOIL_MIN_PCT       10.0f
#define SOIL_MAX_PCT       92.0f
#define TEMP_MAX_C         40.0f
#define PH_MIN             4.5f
#define PH_MAX             8.5f
#define GAS_MAX_PPM        400.0f

// ── Veri Paketi (13 byte) ────────────────────────────────────────────────────
struct __attribute__((packed)) SensorPacket {
    uint16_t node_id;           // Node kimlik numarası
    int16_t  temp_x10;          // °C × 10  (225 → 22.5°C)
    uint16_t soil_x10;          // % × 10
    uint16_t ph_x100;           // pH × 100 (680 → 6.80)
    uint16_t gas_ppm;           // ppm
    uint16_t cap_mv;            // kapasitör mV
    uint8_t  flags;             // bit0=anomali, bit1=acil_iletim
};

// ── Deep Sleep'te Korunan Değişkenler ───────────────────────────────────────
RTC_DATA_ATTR uint32_t wakeCount  = 0;
RTC_DATA_ATTR uint32_t lastTxWake = 0;

// ── Nesneler ─────────────────────────────────────────────────────────────────
OneWire           oneWire(PIN_TEMP_DATA);
DallasTemperature ds18b20(&oneWire);
LoRaDriver        lora(PIN_LORA_SS, PIN_LORA_RST, PIN_LORA_DIO0);

// ── Sensör Fonksiyonları ─────────────────────────────────────────────────────

float readSoilMoisture() {
    // Kalibrasyon: kuru ortam ADC ≈ 2800, ıslak ≈ 1200
    // Kendi sensörünle ölçerek ayarla!
    const int DRY = 2800, WET = 1200;
    int raw = analogRead(PIN_SOIL_MOISTURE);
    float pct = (float)(raw - DRY) / (WET - DRY) * 100.0f;
    return constrain(pct, 0.0f, 100.0f);
}

float readPH() {
    // pH modülü: 0–3.3V → pH 0–14
    // pH=7 → ~2.5V (modüle göre değişir, offset kalibrasyonu gerekli)
    float v = analogRead(PIN_PH) * (3.3f / 4095.0f);
    return constrain(7.0f + (2.5f - v) * 3.5f, 0.0f, 14.0f);
}

float readGasPPM() {
    // MQ-135 basitleştirilmiş model (Rs/R0 oranı)
    // R0: temiz havada kalibrasyon değeri (~3.7 kΩ tipik)
    float v  = analogRead(PIN_GAS) * (3.3f / 4095.0f);
    float rs = (v > 0.01f) ? ((3.3f - v) / v * 10.0f) : 999.0f;  // RL=10kΩ
    float ppm = 116.6f * powf(rs / 3.7f, -2.769f);
    return constrain(ppm, 0.0f, 5000.0f);
}

float readCapVoltage() {
    return analogRead(PIN_CAP_SENSE) * (3.3f / 4095.0f) * CAP_DIVIDER;
}

// ── Anomali Kontrolü ─────────────────────────────────────────────────────────

bool isAnomaly(float soil, float temp, float ph, float gas) {
    return (soil < SOIL_MIN_PCT || soil > SOIL_MAX_PCT ||
            temp > TEMP_MAX_C   ||
            ph   < PH_MIN       || ph > PH_MAX ||
            gas  > GAS_MAX_PPM);
}

// ── İletim Karar Mantığı ─────────────────────────────────────────────────────

enum TxDecision { TX_SKIP, TX_NORMAL, TX_EMERGENCY };

TxDecision decideTx(float cap_v, bool anomaly) {
    if (cap_v < CAP_EMRG_V)  return TX_SKIP;          // Enerji yok
    if (anomaly)              return TX_EMERGENCY;     // Anomali → acil
    if (cap_v >= CAP_TX_MIN_V) return TX_NORMAL;       // Yeterli enerji
    // Çok uzun süre sessizlik → zorla gönder
    if ((wakeCount - lastTxWake) >= FORCE_TX_WAKES)    return TX_NORMAL;
    return TX_SKIP;
}

// ── Setup ────────────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    delay(50);

    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);  // 0–3.3V aralığı

    wakeCount++;
    Serial.printf("\n=== Uyanma #%u ===\n", wakeCount);

    // Sensör ölçümleri
    ds18b20.begin();
    ds18b20.requestTemperatures();
    float temp  = ds18b20.getTempCByIndex(0);
    float soil  = readSoilMoisture();
    float ph    = readPH();
    float gas   = readGasPPM();
    float cap_v = readCapVoltage();

    Serial.printf("  Toprak nem : %.1f %%\n",  soil);
    Serial.printf("  Sıcaklık   : %.1f °C\n",  temp);
    Serial.printf("  pH         : %.2f\n",      ph);
    Serial.printf("  Gaz        : %.0f ppm\n",  gas);
    Serial.printf("  Kap voltaj : %.2f V\n",    cap_v);

    bool anomaly     = isAnomaly(soil, temp, ph, gas);
    TxDecision tx    = decideTx(cap_v, anomaly);

    Serial.printf("  Anomali    : %s\n", anomaly ? "EVET 🚨" : "Hayır");
    Serial.printf("  TX kararı  : %s\n",
        tx == TX_SKIP      ? "ATLA" :
        tx == TX_NORMAL    ? "GÖNDER" : "ACİL GÖNDER");

    if (tx != TX_SKIP) {
        if (lora.begin(433E6)) {
            SensorPacket pkt = {
                .node_id   = 1,
                .temp_x10  = (int16_t)(temp  * 10),
                .soil_x10  = (uint16_t)(soil * 10),
                .ph_x100   = (uint16_t)(ph   * 100),
                .gas_ppm   = (uint16_t)gas,
                .cap_mv    = (uint16_t)(cap_v * 1000),
                .flags     = (uint8_t)((anomaly ? 0x01 : 0) | (tx == TX_EMERGENCY ? 0x02 : 0)),
            };
            int sent = lora.sendPacket((uint8_t*)&pkt, sizeof(pkt));
            Serial.printf("  Gönderildi : %d byte\n", sent);
            lastTxWake = wakeCount;
        } else {
            Serial.println("  LoRa HATA — iletim atlandı");
        }
        lora.sleep();
    }

    Serial.printf("Deep sleep: %llu µs\n\n", SLEEP_US);
    Serial.flush();
    esp_deep_sleep(SLEEP_US);
}

void loop() {
    // Deep sleep → loop hiç çalışmaz
}
