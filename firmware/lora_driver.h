/*
 * lora_driver.h — LoRa (SX1278/Ra-02) Sürücü Sarmalayıcı
 * LoRa kütüphanesi bağımlılığı: sandeepmistry/arduino-LoRa
 * Arduino Library Manager: "LoRa" by Sandeep Mistry
 */

#pragma once
#include <Arduino.h>

class LoRaDriver {
public:
    LoRaDriver(int pin_ss, int pin_rst, int pin_dio0);

    // Başlat. Başarılıysa true döner.
    bool begin(long frequency = 433E6);

    // Bayt dizisi gönder. Dönen değer: gönderilen bayt sayısı, hata = -1
    int sendPacket(const uint8_t* data, size_t len);

    // Uyku moduna al (tüketim: ~0.2 µA)
    void sleep();

    // Uyku modundan çık
    void wake();

    // Sinyal gücü ayarla (2–20 dBm)
    void setTxPower(int dbm);

    // Alınan son paketin RSSI değeri (dBm)
    int lastRSSI();

private:
    int _pin_ss;
    int _pin_rst;
    int _pin_dio0;
    bool _initialized = false;
};
