/*
 * lora_driver.cpp — LoRa Sürücü Implementasyonu
 *
 * Bağımlılık: sandeepmistry/arduino-LoRa
 *   platformio.ini → lib_deps = sandeepmistry/LoRa@^0.8.0
 *   Arduino IDE    → Library Manager → "LoRa" by Sandeep Mistry
 */

#include "lora_driver.h"
#include <LoRa.h>

LoRaDriver::LoRaDriver(int pin_ss, int pin_rst, int pin_dio0)
    : _pin_ss(pin_ss), _pin_rst(pin_rst), _pin_dio0(pin_dio0) {}

bool LoRaDriver::begin(long frequency) {
    LoRa.setPins(_pin_ss, _pin_rst, _pin_dio0);

    if (!LoRa.begin(frequency)) {
        Serial.println("[LoRa] Başlatma başarısız");
        _initialized = false;
        return false;
    }

    // Düşük güç tüketimi için optimize ayarlar
    LoRa.setSpreadingFactor(7);          // SF7: hız/menzil dengesi
    LoRa.setSignalBandwidth(125E3);      // 125 kHz
    LoRa.setCodingRate4(5);              // 4/5
    LoRa.setTxPower(14);                 // 14 dBm ≈ 25 mW
    LoRa.enableCrc();                    // CRC hata denetimi

    _initialized = true;
    Serial.println("[LoRa] Hazır");
    return true;
}

int LoRaDriver::sendPacket(const uint8_t* data, size_t len) {
    if (!_initialized) return -1;

    if (!LoRa.beginPacket()) {
        Serial.println("[LoRa] beginPacket HATA");
        return -1;
    }

    size_t written = LoRa.write(data, len);
    LoRa.endPacket();   // Bloke edici gönderim
    return (int)written;
}

void LoRaDriver::sleep() {
    if (_initialized) LoRa.sleep();
}

void LoRaDriver::wake() {
    if (_initialized) LoRa.idle();
}

void LoRaDriver::setTxPower(int dbm) {
    LoRa.setTxPower(constrain(dbm, 2, 20));
}

int LoRaDriver::lastRSSI() {
    return LoRa.packetRssi();
}
