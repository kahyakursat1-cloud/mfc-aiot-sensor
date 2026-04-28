"""
LoRa İletim Modeli
==================
LoRa parametrelerine göre havada kalma süresi (ToA), enerji maliyeti
ve link bütçesi (menzil) hesabı.

Kullanım:
    python transmission_model.py
"""

import math
from dataclasses import dataclass


@dataclass
class LoRaConfig:
    frequency_mhz: float = 433.0    # MHz (Ra-02 modül)
    tx_power_dbm: float = 14        # dBm ≈ 25 mW
    bandwidth_khz: float = 125      # kHz
    spreading_factor: int = 7       # SF7–SF12
    coding_rate: int = 5            # 4/5 → denominator
    preamble_sym: int = 8           # standart preamble
    payload_bytes: int = 13         # SensorPacket boyutu (firmware ile eşleşmeli)
    tx_current_ma: float = 120      # mA TX sırasında
    rx_current_ma: float = 12       # mA RX bekleme
    sleep_current_ua: float = 0.2   # µA uyku hali
    vcc: float = 3.3                # V

    # Anten kazancı ve kablo kaybı
    tx_antenna_gain_dbi: float = 2.0
    rx_antenna_gain_dbi: float = 2.0
    cable_loss_db: float = 0.5

    @property
    def symbol_duration_ms(self) -> float:
        bw_hz = self.bandwidth_khz * 1000
        return (2 ** self.spreading_factor / bw_hz) * 1000

    @property
    def time_on_air_ms(self) -> float:
        """LoRa ToA — Semtech AN1200.13 formülü."""
        sf = self.spreading_factor
        bw_hz = self.bandwidth_khz * 1000
        # Header aktif, düşük veri hızı optimize (LDR): SF≥11 && BW=125kHz
        ldr = 1 if (sf >= 11 and self.bandwidth_khz <= 125) else 0
        de = ldr

        n_payload = max(0, math.ceil(
            (8 * self.payload_bytes - 4 * sf + 28 + 16 - 20 * 0) /
            (4 * (sf - 2 * de))
        )) * self.coding_rate

        n_sym_total = (self.preamble_sym + 4.25) + 8 + n_payload
        return n_sym_total * self.symbol_duration_ms

    @property
    def tx_energy_mj(self) -> float:
        """TX başına harcanan enerji (mJ) — sadece RF kısmı."""
        return self.tx_current_ma * self.vcc * (self.time_on_air_ms / 1000)

    @property
    def rx_energy_mj(self) -> float:
        """ACK bekleme enerji maliyeti (~500ms RX penceresi)."""
        return self.rx_current_ma * self.vcc * 0.5

    @property
    def total_tx_cycle_energy_mj(self) -> float:
        return self.tx_energy_mj + self.rx_energy_mj

    def path_loss_db(self, distance_m: float, env: str = 'suburban') -> float:
        """Log-distance yol kaybı modeli."""
        exponents = {'los': 2.0, 'suburban': 2.7, 'urban': 3.5, 'indoor': 4.0}
        n = exponents.get(env, 2.7)
        wl = 3e8 / (self.frequency_mhz * 1e6)
        pl_1m = 20 * math.log10(4 * math.pi / wl)
        return pl_1m + 10 * n * math.log10(max(distance_m, 1))

    def sensitivity_dbm(self) -> float:
        """Alıcı hassasiyeti — SF'ye göre yaklaşık değer."""
        return -124 - 2.5 * (self.spreading_factor - 7)

    def link_budget(self, distance_m: float, env: str = 'suburban') -> dict:
        eirp = self.tx_power_dbm + self.tx_antenna_gain_dbi - self.cable_loss_db
        pl = self.path_loss_db(distance_m, env)
        rx_power = eirp - pl + self.rx_antenna_gain_dbi
        sens = self.sensitivity_dbm()
        margin = rx_power - sens
        return {
            'eirp_dbm': eirp,
            'path_loss_db': pl,
            'rx_power_dbm': rx_power,
            'sensitivity_dbm': sens,
            'link_margin_db': margin,
            'can_link': margin > 0,
        }

    def max_range_m(self, env: str = 'suburban') -> int:
        """Link marjı = 0 olan maksimum menzil."""
        for d in range(10, 50_001, 10):
            if not self.link_budget(d, env)['can_link']:
                return d - 10
        return 50_000


def print_sf_comparison():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║          Spreading Factor Karşılaştırması (433 MHz)         ║")
    print("╠════╦══════════╦════════════╦══════════╦══════════╦══════════╣")
    print("║ SF ║  ToA(ms) ║  Enerji(mJ)║  Hassas. ║ Suburban ║  LoS    ║")
    print("╠════╬══════════╬════════════╬══════════╬══════════╬══════════╣")
    for sf in range(7, 13):
        l = LoRaConfig(spreading_factor=sf)
        max_sub = l.max_range_m('suburban')
        max_los = l.max_range_m('los')
        print(f"║ {sf:<2} ║ {l.time_on_air_ms:>8.1f} ║ {l.total_tx_cycle_energy_mj:>10.2f} "
              f"║ {l.sensitivity_dbm():>6.0f}dBm ║ {max_sub:>5}m   ║ {max_los:>5}m  ║")
    print("╚════╩══════════╩════════════╩══════════╩══════════╩══════════╝")


def print_link_sweep(config: LoRaConfig):
    distances = [50, 100, 250, 500, 1000, 2000, 5000]
    print(f"\n  SF{config.spreading_factor} Link Bütçesi (suburban)")
    print(f"  {'Mesafe':>8}  {'Kayıp':>8}  {'RX':>8}  {'Marj':>7}  {'OK':>4}")
    print(f"  {'-'*45}")
    for d in distances:
        lb = config.link_budget(d, 'suburban')
        ok = '✅' if lb['can_link'] else '❌'
        print(f"  {d:>6}m   {lb['path_loss_db']:>6.1f}dB  {lb['rx_power_dbm']:>6.1f}dBm  "
              f"{lb['link_margin_db']:>5.1f}dB  {ok}")


if __name__ == '__main__':
    default = LoRaConfig(spreading_factor=7, payload_bytes=13)

    print("=== LoRa İletim Modeli ===")
    print(f"  Sembol süresi   : {default.symbol_duration_ms:.2f} ms")
    print(f"  Havada kalma    : {default.time_on_air_ms:.1f} ms")
    print(f"  TX enerji       : {default.tx_energy_mj:.2f} mJ")
    print(f"  TX+RX toplam    : {default.total_tx_cycle_energy_mj:.2f} mJ")
    print(f"  Maks menzil(sub): {default.max_range_m('suburban')} m")

    print_link_sweep(default)
    print_sf_comparison()
