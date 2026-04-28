"""
Sensör Node Davranış Modeli
ESP32 deep-sleep döngüsünü simüle eder.
"""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class SensorReading:
    soil_moisture: float   # 0–100 %
    temperature_c: float   # °C
    ph: float              # 0–14
    gas_ppm: float         # ppm


# Enerji maliyetleri (Joule)
COST = {
    "sleep":    0.00001,   # ~10 µW × 1s
    "measure":  0.001,     # 80mA × 3.3V × ~4ms toplam ölçüm
    "transmit": 0.050,     # 120mA × 3.3V × ~125ms LoRa ToA
}


class SensorNode:
    def __init__(self, node_id: int = 1):
        self.node_id = node_id
        self.last_reading: Optional[SensorReading] = None
        self.tx_count = 0
        self.tx_failed = 0

    def read_sensors(self) -> SensorReading:
        """Gerçekçi dağılımla rastgele sensör verisi üret."""
        return SensorReading(
            soil_moisture=max(0, min(100, random.gauss(45, 12))),
            temperature_c=max(-5, min(55, random.gauss(22, 5))),
            ph=max(0, min(14, random.gauss(6.8, 0.6))),
            gas_ppm=max(0, random.expovariate(1 / 60)),
        )

    def step(self, capacitor, decision: str) -> dict:
        """
        Tek simülasyon adımı.
        Döndürür: {'decision', 'success', 'reading'}
        """
        result = {"decision": decision, "success": False, "reading": None}

        if decision == "sleep":
            capacitor.consume(COST["sleep"])
            result["success"] = True

        elif decision == "measure":
            if capacitor.consume(COST["measure"]):
                self.last_reading = self.read_sensors()
                result["reading"] = self.last_reading
                result["success"] = True

        elif decision == "transmit":
            if capacitor.consume(COST["transmit"]):
                self.last_reading = self.read_sensors()
                result["reading"] = self.last_reading
                result["success"] = True
                self.tx_count += 1
            else:
                self.tx_failed += 1

        return result
