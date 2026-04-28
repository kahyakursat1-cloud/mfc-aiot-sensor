"""
Veri Kaynağı
=============
Üç mod:
  1. DEMO   — simulation/ modülleri varsa gerçekçi fizik simülasyonu
  2. RANDOM — simulation/ yoksa salt rastgele veri
  3. SERIAL — gerçek ESP32 (COM port, ayrı thread)

Dashboard sadece bu modülden veri okur; kaynak değişince tek satır değişir.
"""

import sys
import os
import random
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import numpy as np

# simulation/ ve ai/ modüllerini bul
_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, _ROOT)

try:
    from simulation.mfc_model import MFC
    from simulation.energy_storage import SuperCapacitor
    _SIM_OK = True
except ImportError:
    _SIM_OK = False

try:
    from ai.decision_model import DecisionModel
    _AI_OK = True
except ImportError:
    _AI_OK = False


# ── Veri modeli ───────────────────────────────────────────────────────────────

@dataclass
class NodeReading:
    node_id:        int
    timestamp:      str
    soil_moisture:  float   # 0–100 %
    temperature_c:  float   # °C
    ph:             float   # 0–14
    gas_ppm:        float   # ppm
    cap_voltage:    float   # 0–2.7 V
    decision:       str     = "sleep"   # sleep / measure / transmit
    is_anomaly:     bool    = False
    anomaly_type:   str     = ""

    @property
    def soc(self) -> float:
        return min(1.0, max(0.0, self.cap_voltage / 2.7))

    @staticmethod
    def _check_anomaly(sm, tc, ph, gas):
        if sm  <  10.0: return True, "kuraklık"
        if sm  >  92.0: return True, "su baskını"
        if tc  >  40.0: return True, "yüksek sıcaklık"
        if ph  <   4.5: return True, "pH düşük"
        if ph  >   8.5: return True, "pH yüksek"
        if gas >  400.0: return True, "gaz sızıntısı"
        return False, ""


# ── Simüle edilen tek node ────────────────────────────────────────────────────

class _SimNode:
    """Bir sensör node'unun fizik + AI simülasyonu."""

    def __init__(self, node_id: int, ai_model: Optional["DecisionModel"] = None):
        self.node_id = node_id
        self.ai = ai_model
        # Her node biraz farklı MFC karakteri
        rate = random.uniform(0.0003, 0.0008)
        self.mfc  = MFC(generation_rate=rate) if _SIM_OK else None
        self.cap  = SuperCapacitor(capacity=1.0) if _SIM_OK else None
        if self.cap:
            self.cap.energy = random.uniform(0.2, 0.9)
        # Anomali enjeksiyonu için sayaç
        self._anomaly_counter = random.randint(30, 120)

    def tick(self) -> NodeReading:
        now = datetime.now().strftime("%H:%M:%S")

        # ── Enerji ─────────────────────────────────────────────
        if self.mfc and self.cap:
            self.cap.charge(self.mfc.generate_energy())
            cap_v = self.cap.energy / self.cap.capacity * 2.7
        else:
            cap_v = random.uniform(1.0, 2.7)

        # ── Sensör okumaları ───────────────────────────────────
        sm  = float(np.clip(np.random.normal(45, 10), 0, 100))
        tc  = float(np.clip(np.random.normal(22,  5), -5, 55))
        ph  = float(np.clip(np.random.normal(6.8, 0.5), 0, 14))
        gas = float(max(0, np.random.exponential(50)))

        # Belirli aralıklarla anomali enjekte et
        self._anomaly_counter -= 1
        if self._anomaly_counter <= 0:
            atype = random.choice(["drought", "ph_low", "gas", "heat"])
            if atype == "drought":  sm  = random.uniform(2, 8)
            elif atype == "ph_low": ph  = random.uniform(3.0, 4.0)
            elif atype == "gas":    gas = random.uniform(500, 1200)
            elif atype == "heat":   tc  = random.uniform(42, 50)
            self._anomaly_counter = random.randint(40, 150)

        # ── AI kararı ──────────────────────────────────────────
        decision = "measure"
        if self.ai:
            try:
                decision = self.ai.predict(
                    energy   = min(1.0, cap_v / 2.7),
                    moisture = sm / 100,
                    temp     = tc / 55,
                    ph       = ph / 14,
                )
            except Exception:
                decision = "measure"

        # TX varsa kapasitörü deşarj et
        if decision == "transmit" and self.cap:
            self.cap.consume(0.05)

        is_anom, atype_str = NodeReading._check_anomaly(sm, tc, ph, gas)

        return NodeReading(
            node_id       = self.node_id,
            timestamp     = now,
            soil_moisture = round(sm,  1),
            temperature_c = round(tc,  1),
            ph            = round(ph,  2),
            gas_ppm       = round(gas, 1),
            cap_voltage   = round(cap_v, 3),
            decision      = decision,
            is_anomaly    = is_anom,
            anomaly_type  = atype_str,
        )


# ── Ana DataSource ────────────────────────────────────────────────────────────

class DataSource:
    """
    Dashboard'ın veri kaynağı.

    Kullanım:
        ds = DataSource(n_nodes=3)
        readings = ds.tick()          # Anlık okuma listesi al
        history  = ds.history(1, 'ph', n=100)   # Node 1 pH geçmişi
    """

    MAX_HISTORY = 300

    def __init__(self, n_nodes: int = 3, interval_ms: int = 1000):
        self.n_nodes     = n_nodes
        self.interval_ms = interval_ms

        # AI modeli (paylaşımlı)
        self._ai: Optional[DecisionModel] = None
        if _AI_OK:
            try:
                self._ai = DecisionModel()
                self._ai.train()
                print("[DataSource] AI karar modeli hazır")
            except Exception as e:
                print(f"[DataSource] AI yüklenemedi: {e}")

        # Node simülatörleri
        self._sim_nodes = [_SimNode(i + 1, self._ai) for i in range(n_nodes)]

        # Geçmiş tamponları: {node_id: deque[NodeReading]}
        self._history: dict[int, deque] = {
            i + 1: deque(maxlen=self.MAX_HISTORY) for i in range(n_nodes)
        }

        # Son okumalar
        self._latest: list[NodeReading] = []
        self._lock = threading.Lock()

        # Arka plan güncelleme thread'i
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Arka plan veri güncelleme thread'ini başlat."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[DataSource] {self.n_nodes} node simülasyonu başlatıldı")

    def stop(self):
        self._running = False

    def tick(self) -> list[NodeReading]:
        """Tüm node'lardan tek seferlik okuma yap (thread güvenli)."""
        readings = [n.tick() for n in self._sim_nodes]
        with self._lock:
            self._latest = readings
            for r in readings:
                self._history[r.node_id].append(r)
        return readings

    def latest(self) -> list[NodeReading]:
        """Son hesaplanan okuma listesini döndür."""
        with self._lock:
            return list(self._latest)

    def history(self, node_id: int, attr: str, n: int = 200) -> np.ndarray:
        """Belirtilen node ve özellik için son n değeri dizisi."""
        with self._lock:
            buf = list(self._history.get(node_id, []))
        vals = [getattr(r, attr) for r in buf[-n:]]
        return np.array(vals, dtype=float)

    def anomalies(self, last_n: int = 50) -> list[dict]:
        """Tüm node'lardaki anomali kayıtları (yeniden eskiye)."""
        events = []
        with self._lock:
            for nid, buf in self._history.items():
                for r in buf:
                    if r.is_anomaly:
                        events.append({
                            "node":  nid,
                            "time":  r.timestamp,
                            "type":  r.anomaly_type,
                            "ph":    r.ph,
                            "gas":   r.gas_ppm,
                            "soil":  r.soil_moisture,
                        })
        events.sort(key=lambda x: x["time"], reverse=True)
        return events[:last_n]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _loop(self):
        while self._running:
            self.tick()
            time.sleep(self.interval_ms / 1000)
