"""
MFC + AIoT Node Tam Simülasyonu
================================
Eşdeğer devre modeli kullanarak MFC güç çıkışını, süper kapasitör şarj/deşarj
döngüsünü ve ESP32 iletim başarı oranını simüle eder.

Kullanım:
    python mfc_simulation.py
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class MFCParams:
    emf_theoretical: float = 1.14      # V — asetat oksidasyonu için teorik EMF
    activation_loss: float = 0.25      # V — aktivasyon aşımı
    internal_resistance: float = 150   # Ω — hücre iç direnci
    area_m2: float = 0.01              # m² — elektrot yüzey alanı
    substrate_initial: float = 1.5     # g/L — başlangıç substrat konsantrasyonu
    substrate_decay: float = 0.03      # g/L/saat — tüketim hızı
    temperature_c: float = 30          # °C


@dataclass
class CapacitorState:
    capacitance: float = 1.0    # Farad
    max_voltage: float = 2.7    # V
    voltage: float = 0.1        # V — başlangıç

    @property
    def energy_j(self) -> float:
        return 0.5 * self.capacitance * self.voltage ** 2

    @property
    def soc(self) -> float:
        return self.voltage / self.max_voltage


class MFCSimulation:
    def __init__(self, mfc: MFCParams, cap: CapacitorState):
        self.mfc = mfc
        self.cap = cap
        self.time_h: List[float] = []
        self.ocv_log: List[float] = []
        self.power_uw_log: List[float] = []
        self.cap_v_log: List[float] = []
        self.substrate_log: List[float] = []

    def _ocv(self, substrate: float) -> float:
        """Nernst tabanlı açık devre voltajı."""
        if substrate <= 0:
            return 0.0
        s = max(substrate, 1e-6)
        return self.mfc.emf_theoretical + 0.0257 * np.log(s)

    def _step(self, dt_s: float, substrate: float) -> Tuple[float, float]:
        """
        Tek zaman adımı.
        Döndürür: (güç_µW, yeni_substrat_g/L)
        """
        v_cap = self.cap.voltage
        ocv = self._ocv(substrate)

        # Kapasitör şarj akımı (v_cap < ocv ise akar)
        if ocv > v_cap:
            current = (ocv - self.mfc.activation_loss - v_cap) / (
                self.mfc.internal_resistance + 10)  # 10Ω kablo
            current = max(0.0, current)
        else:
            current = 0.0

        v_cell = ocv - self.mfc.activation_loss - current * self.mfc.internal_resistance
        power_uw = max(0.0, v_cell * current * 1e6)

        # Kapasitörü şarj et
        dv = (current * dt_s) / self.cap.capacitance
        self.cap.voltage = min(self.cap.voltage + dv, self.cap.max_voltage)

        # Substrat tüketimi (Monod kinetik)
        k_half = 0.5
        rate = self.mfc.substrate_decay * substrate / (substrate + k_half)
        substrate_new = max(0.0, substrate - rate * dt_s / 3600)

        return power_uw, substrate_new

    def run(
        self,
        duration_hours: float = 48,
        dt_seconds: float = 60,
        wake_interval_s: float = 600,    # ESP32 uyanma periyodu
        tx_energy_mj: float = 50,        # LoRa TX başına enerji maliyeti
    ) -> dict:
        """
        Tam simülasyon çalıştır.
        Döndürür: istatistik sözlüğü.
        """
        t = 0.0
        substrate = self.mfc.substrate_initial
        next_wake = wake_interval_s
        tx_ok = 0
        tx_fail = 0

        while t <= duration_hours * 3600:
            power_uw, substrate = self._step(dt_seconds, substrate)

            # ESP32 uyandı mı?
            if t >= next_wake:
                needed_j = tx_energy_mj * 1e-3
                if self.cap.energy_j >= needed_j:
                    # Kapasitörü deşarj et
                    e_new = self.cap.energy_j - needed_j
                    self.cap.voltage = np.sqrt(2 * e_new / self.cap.capacitance)
                    tx_ok += 1
                else:
                    tx_fail += 1
                next_wake += wake_interval_s

            self.time_h.append(t / 3600)
            self.ocv_log.append(self._ocv(substrate))
            self.power_uw_log.append(power_uw)
            self.cap_v_log.append(self.cap.voltage)
            self.substrate_log.append(substrate)

            t += dt_seconds

        return {
            'tx_ok': tx_ok,
            'tx_fail': tx_fail,
            'success_rate': tx_ok / max(1, tx_ok + tx_fail),
            'avg_power_uw': float(np.mean(self.power_uw_log)),
            'final_substrate_g_L': substrate,
        }

    def plot(self, save_path: str = 'simulation_results.png'):
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('MFC + AIoT Node Simülasyonu', fontsize=14, fontweight='bold')

        axes[0, 0].plot(self.time_h, self.ocv_log, 'steelblue')
        axes[0, 0].set(xlabel='Zaman (saat)', ylabel='OCV (V)',
                       title='MFC Açık Devre Voltajı')
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].plot(self.time_h, self.power_uw_log, 'tomato')
        axes[0, 1].set(xlabel='Zaman (saat)', ylabel='Güç (µW)',
                       title='MFC Güç Çıkışı')
        axes[0, 1].grid(True, alpha=0.3)

        axes[1, 0].plot(self.time_h, self.cap_v_log, 'seagreen')
        axes[1, 0].axhline(2.7, color='red', ls='--', lw=1, label='Maks 2.7V')
        axes[1, 0].axhline(1.8, color='orange', ls='--', lw=1, label='Min TX 1.8V')
        axes[1, 0].set(xlabel='Zaman (saat)', ylabel='Voltaj (V)',
                       title='Süper Kapasitör Durumu')
        axes[1, 0].legend(fontsize=8)
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].plot(self.time_h, self.substrate_log, 'mediumpurple')
        axes[1, 1].set(xlabel='Zaman (saat)', ylabel='Substrat (g/L)',
                       title='Bakteri Substratı Tüketimi')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"Grafik kaydedildi: {save_path}")
        plt.show()


def run_parameter_sweep():
    """Farklı MFC parametrelerini karşılaştır."""
    configs = [
        ("Düşük verim",  100, 1.0),
        ("Orta verim",   150, 1.5),
        ("Yüksek verim", 200, 2.0),
    ]
    print(f"\n{'Konfigürasyon':<20} {'Ort Güç (µW)':>14} {'TX Başarı':>12} {'TX Başarısız':>14}")
    print("-" * 62)
    for name, r_int, substrate in configs:
        mfc = MFCParams(internal_resistance=r_int, substrate_initial=substrate)
        cap = CapacitorState(capacitance=1.0, voltage=0.1)
        sim = MFCSimulation(mfc, cap)
        res = sim.run(duration_hours=24)
        print(f"{name:<20} {res['avg_power_uw']:>14.1f} {res['tx_ok']:>12} {res['tx_fail']:>14}")


if __name__ == '__main__':
    mfc = MFCParams(internal_resistance=150, substrate_initial=1.5, substrate_decay=0.03)
    cap = CapacitorState(capacitance=1.0, voltage=0.1)

    sim = MFCSimulation(mfc, cap)
    results = sim.run(
        duration_hours=48,
        dt_seconds=60,
        wake_interval_s=600,   # 10 dakikada bir uyan
        tx_energy_mj=50,       # LoRa TX için 50 mJ
    )

    print("=== 48 Saatlik Simülasyon Sonuçları ===")
    print(f"  Başarılı iletim  : {results['tx_ok']}")
    print(f"  Başarısız iletim : {results['tx_fail']}")
    print(f"  Başarı oranı     : {results['success_rate']:.1%}")
    print(f"  Ortalama güç     : {results['avg_power_uw']:.1f} µW")
    print(f"  Son substrat     : {results['final_substrate_g_L']:.3f} g/L")

    sim.plot()
    run_parameter_sweep()
