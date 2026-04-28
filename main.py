"""
Mikrobiyal AIoT Sensör Ağı — Ana Simülasyon
=============================================
MFC → Süper Kapasitör → AI Karar → Sensör Node → Grafik

Kullanım:
    python main.py
    python main.py --steps 500 --rate 0.0008
"""

import argparse
import random
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from simulation.mfc_model import MFC
from simulation.energy_storage import SuperCapacitor
from simulation.sensor_node import SensorNode
from ai.decision_model import DecisionModel


def run_simulation(n_steps: int = 1000, generation_rate: float = 0.0005) -> dict:
    # ── Bileşenleri başlat ─────────────────────────────────────────────────
    mfc  = MFC(generation_rate=generation_rate)
    cap  = SuperCapacitor(capacity=1.0)
    node = SensorNode(node_id=1)
    ai   = DecisionModel()

    print("AI modeli eğitiliyor...")
    ai.train()

    # ── Log listeleri ──────────────────────────────────────────────────────
    energy_log    = []
    soc_log       = []
    action_log    = []
    soil_log      = []
    temp_log      = []
    ph_log        = []
    anomaly_times = []

    # Anomali eşikleri (ham değer, 0–100 / °C / pH)
    SOIL_MIN, SOIL_MAX = 10.0, 90.0
    TEMP_MAX           = 38.0
    PH_MIN, PH_MAX     = 4.5, 8.5

    print(f"Simülasyon başlatıldı: {n_steps} adım\n")

    for t in range(n_steps):
        # 1. MFC enerji üret ve kapasitörü şarj et
        produced = mfc.generate_energy()
        cap.charge(produced)

        # 2. Çevresel ölçümler (simüle)
        moisture = max(0, min(100, random.gauss(45, 12)))
        temp     = max(-5, min(55, random.gauss(22, 5)))
        ph       = max(0, min(14, random.gauss(6.8, 0.6)))

        # 3. AI karar ver (normalize edilmiş girişler)
        decision = ai.predict(
            energy   = cap.soc,
            moisture = moisture / 100,
            temp     = temp / 55,
            ph       = ph / 14,
        )

        # 4. Node çalıştır
        result = node.step(cap, decision)

        # Anomali var mı?
        is_anomaly = (
            moisture < SOIL_MIN or moisture > SOIL_MAX or
            temp     > TEMP_MAX or
            ph       < PH_MIN   or ph > PH_MAX
        )
        if is_anomaly:
            anomaly_times.append(t)
            # Anomalide enerji yetiyorsa zorla gönder
            if decision != "transmit" and cap.soc > 0.35:
                node.step(cap, "transmit")

        # 5. Log
        energy_log.append(cap.energy)
        soc_log.append(cap.soc)
        action_log.append(decision)
        soil_log.append(moisture)
        temp_log.append(temp)
        ph_log.append(ph)

    # ── Özet ──────────────────────────────────────────────────────────────
    tx_count  = action_log.count("transmit")
    msr_count = action_log.count("measure")
    slp_count = action_log.count("sleep")

    print(f"{'─'*40}")
    print(f"Toplam adım      : {n_steps}")
    print(f"İletim (transmit): {tx_count}  ({tx_count/n_steps:.1%})")
    print(f"Ölçüm  (measure) : {msr_count}  ({msr_count/n_steps:.1%})")
    print(f"Uyku   (sleep)   : {slp_count}  ({slp_count/n_steps:.1%})")
    print(f"Anomali tespiti  : {len(anomaly_times)}")
    print(f"Başarısız TX     : {node.tx_failed}")
    print(f"Son SOC          : {cap.soc:.1%}")
    print(f"{'─'*40}\n")

    return {
        "energy_log": energy_log,
        "soc_log": soc_log,
        "action_log": action_log,
        "soil_log": soil_log,
        "temp_log": temp_log,
        "ph_log": ph_log,
        "anomaly_times": anomaly_times,
        "tx_count": tx_count,
        "anomaly_count": len(anomaly_times),
    }


def plot_results(data: dict, save_path: str = "simulation_results.png"):
    steps = range(len(data["energy_log"]))
    actions = data["action_log"]

    # Eylem renk haritası
    color_map = {"sleep": "lightgray", "measure": "steelblue", "transmit": "seagreen"}
    action_colors = [color_map.get(a, "black") for a in actions]

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle("Mikrobiyal AIoT Sensör Ağı — Simülasyon", fontsize=14, fontweight="bold")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    # 1. Enerji seviyesi
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(steps, data["soc_log"], color="seagreen", lw=1.2, label="SOC")
    ax1.axhline(0.55, color="orange", ls="--", lw=1, label="İletim eşiği")
    ax1.axhline(0.25, color="red",    ls="--", lw=1, label="Uyku eşiği")
    for t in data["anomaly_times"]:
        ax1.axvline(t, color="red", alpha=0.15, lw=0.8)
    ax1.set(xlabel="Adım", ylabel="SOC (0–1)", title="Süper Kapasitör Durumu + Anomaliler (kırmızı çizgiler)")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.05)

    # 2. AI kararları (renkli scatter)
    ax2 = fig.add_subplot(gs[1, 0])
    scatter_y = {"sleep": 0, "measure": 1, "transmit": 2}
    y_vals = [scatter_y[a] for a in actions]
    ax2.scatter(steps, y_vals, c=action_colors, s=2, alpha=0.6)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["Uyu", "Ölç", "Gönder"])
    ax2.set(xlabel="Adım", title="AI Karar Dağılımı")
    ax2.grid(True, alpha=0.2)

    # 3. Toprak nemi
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(steps, data["soil_log"], color="saddlebrown", lw=0.8, alpha=0.7)
    ax3.axhline(10, color="red",    ls="--", lw=1, label="Kuraklık eşiği")
    ax3.axhline(90, color="blue",   ls="--", lw=1, label="Baskın eşiği")
    ax3.set(xlabel="Adım", ylabel="%", title="Toprak Nemi")
    ax3.legend(fontsize=7)
    ax3.grid(True, alpha=0.3)

    # 4. Sıcaklık
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(steps, data["temp_log"], color="tomato", lw=0.8, alpha=0.7)
    ax4.axhline(38, color="red", ls="--", lw=1, label="Sıcaklık eşiği")
    ax4.set(xlabel="Adım", ylabel="°C", title="Sıcaklık")
    ax4.legend(fontsize=7)
    ax4.grid(True, alpha=0.3)

    # 5. pH
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.plot(steps, data["ph_log"], color="mediumpurple", lw=0.8, alpha=0.7)
    ax5.axhline(4.5, color="red",    ls="--", lw=1, label="pH min")
    ax5.axhline(8.5, color="orange", ls="--", lw=1, label="pH max")
    ax5.set(xlabel="Adım", ylabel="pH", title="pH Değeri")
    ax5.legend(fontsize=7)
    ax5.grid(True, alpha=0.3)

    plt.savefig(save_path, dpi=150)
    print(f"Grafik kaydedildi: {save_path}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mikrobiyal AIoT Simülasyonu")
    parser.add_argument("--steps", type=int,   default=1000,   help="Simülasyon adım sayısı")
    parser.add_argument("--rate",  type=float, default=0.0005, help="MFC üretim hızı (J/adım)")
    parser.add_argument("--save",  type=str,   default="simulation_results.png")
    args = parser.parse_args()

    data = run_simulation(n_steps=args.steps, generation_rate=args.rate)
    plot_results(data, save_path=args.save)
