"""
Enerji Bütçe Modeli
====================
MFC üretim gücü vs. node tüketim gücü dengesi.
Sistemin kaç dakikalık uyku döngüsüyle sürdürülebilir olduğunu hesaplar.

Kullanım:
    python energy_model.py
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Consumer:
    name: str
    active_current_ma: float   # mA — aktif haldeyken
    active_duration_s: float   # s — döngü başına aktif süre
    idle_current_ua: float     # µA — uyku/bekleme hali
    vcc: float = 3.3           # V

    def avg_power_uw(self, cycle_s: float) -> float:
        """Verilen döngü süresindeki ortalama güç (µW)."""
        active_frac = min(self.active_duration_s / cycle_s, 1.0)
        idle_frac = 1.0 - active_frac
        avg_ma = self.active_current_ma * active_frac + (self.idle_current_ua / 1000) * idle_frac
        return avg_ma * self.vcc * 1000  # → µW


# Bileşen profilleri (gerçekçi değerler, datasheet'ten)
CONSUMERS: List[Consumer] = [
    Consumer("ESP32 (aktif)",            80.0,   5.0,   10.0),
    Consumer("LoRa TX (Ra-02, SF7)",    120.0,   0.1,    0.2),
    Consumer("LoRa RX (ACK bekleme)",    12.0,   0.5,    0.2),
    Consumer("Toprak Nemi Sensörü",       5.0,   2.0,    0.1),
    Consumer("DS18B20 Sıcaklık",          1.5,   1.0,    0.1),
    Consumer("pH Modülü (analog)",       10.0,   2.0,    0.5),
    Consumer("MQ-135 Gaz Sensörü",       35.0,   3.0,    1.5),  # ısınma süresi dahil
]


def analyze(mfc_power_uw: float, cycle_s: float) -> Dict:
    """
    Verilen MFC gücü ve döngü süresi için bütçe analizi.
    """
    breakdown = {c.name: c.avg_power_uw(cycle_s) for c in CONSUMERS}
    total_uw = sum(breakdown.values())
    margin_uw = mfc_power_uw - total_uw
    sustainable = margin_uw > 0
    return {
        'cycle_s': cycle_s,
        'breakdown': breakdown,
        'total_uw': total_uw,
        'mfc_uw': mfc_power_uw,
        'margin_uw': margin_uw,
        'sustainable': sustainable,
    }


def print_budget(mfc_power_uw: float, cycle_s: float):
    r = analyze(mfc_power_uw, cycle_s)
    print(f"\n{'=' * 54}")
    print(f"  Enerji Bütçesi  |  MFC={mfc_power_uw:.0f} µW  |  Döngü={cycle_s:.0f} s")
    print(f"{'=' * 54}")
    print(f"  {'Bileşen':<30} {'µW':>8}")
    print(f"  {'-' * 40}")
    for name, uw in r['breakdown'].items():
        bar = '█' * max(1, int(uw / 5))
        print(f"  {name:<30} {uw:>8.2f}  {bar}")
    print(f"  {'-' * 40}")
    print(f"  {'Toplam Tüketim':<30} {r['total_uw']:>8.2f} µW")
    print(f"  {'MFC Üretim':<30} {r['mfc_uw']:>8.2f} µW")
    print(f"  {'Marj':<30} {r['margin_uw']:>+8.2f} µW")
    print(f"  {'Sürdürülebilir':<30} {'✅ EVET' if r['sustainable'] else '❌ HAYIR':>8}")
    print(f"{'=' * 54}")


def find_min_cycle(mfc_power_uw: float, max_search_s: float = 7200) -> float:
    """
    Verilen MFC gücüyle sürdürülebilir olan minimum döngü süresini bulur.
    (İkili arama)
    """
    lo, hi = 10.0, max_search_s
    for _ in range(40):
        mid = (lo + hi) / 2
        if analyze(mfc_power_uw, mid)['sustainable']:
            hi = mid
        else:
            lo = mid
    return hi


def sweep():
    """MFC güç seviyeleri × döngü süreleri için özet tablo."""
    mfc_levels = [50, 100, 200, 300, 500]
    cycles = [300, 600, 900, 1800]

    header = f"{'MFC (µW)':<10}" + "".join(f"  {c//60:>5}dk" for c in cycles)
    print(f"\n{'=' * len(header)}")
    print("  Sürdürülebilirlik Matrisi  (✅ / ❌)")
    print(f"{'=' * len(header)}")
    print(header)
    print("-" * len(header))
    for uw in mfc_levels:
        row = f"{uw:<10}"
        for c in cycles:
            ok = analyze(uw, c)['sustainable']
            row += f"  {'✅' if ok else '❌':>5} "
        min_cycle = find_min_cycle(uw)
        row += f"   min={min_cycle:.0f}s"
        print(row)


if __name__ == '__main__':
    # Varsayılan analiz
    print_budget(mfc_power_uw=150, cycle_s=600)

    # Kötü senaryo: zayıf MFC
    print_budget(mfc_power_uw=60, cycle_s=1800)

    # Özet matris
    sweep()
