"""
paper/make_figures.py
=====================
Publication figures (600 DPI) for the feasibility-analysis rewrite.
All values match the dimensionally consistent budget and the reproducible
scripts (energy_budget, literature_anchor, monte_carlo, validate_anomaly).

Visual language (shared with fig1_power_path.py): Arial, ink and grey for
structure and secondary series, one blue accent for the quantity the figure is
about, no in-figure titles (captions carry them), unfilled boxes in diagrams.

Usage:
    python paper/make_figures.py
Outputs -> paper/figures/
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch, Polygon

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.energy_chain import (e_event, interval_h, p_net, CASES, cells_for_target,
                                     mc_interval, mc_cells, P_FLOOR, I_TX,
                                     V_CC, I_ACT, I_SENS, E_TX, dynamic_scenario)

DPI = 600
OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

INK, INK2, MUTE, RULE = "#0b0b0b", "#52514e", "#a8a6a0", "#e4e2dc"
BLUE, LBLUE, GREY, DGREY = "#1e78d2", "#8dccfc", "#c9c7c1", "#7d7b75"
CASE = {"ideal": dict(color=DGREY, ls="--", lw=1.2),
        "realistic": dict(color=BLUE, ls="-", lw=2.0),
        "conservative": dict(color=INK, ls=":", lw=1.6)}

plt.rcParams.update({
    "font.family": "Arial", "font.size": 8,
    "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
    "axes.grid": False, "axes.axisbelow": True,
    "axes.edgecolor": INK2, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 8, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 6,
    "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.4, "ytick.minor.width": 0.4,
    "text.color": INK, "legend.frameon": False, "legend.fontsize": 7, "legend.handlelength": 2.4,
    "savefig.bbox": "tight", "savefig.dpi": DPI, "figure.facecolor": "white",
})


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=RULE, lw=0.6, which="major")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig)


def dbox(ax, x, y, w, h, title, body="", ec=INK, tc=INK, bc=INK2, lw=0.9, tfs=7.6, bfs=6.4, gap=0.0):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=ec, lw=lw))
    if body:
        ax.text(x + w / 2, y + h * 0.72 + gap, title, ha="center", va="center", fontsize=tfs, fontweight="bold",
                color=tc, linespacing=1.15)
        ax.text(x + w / 2, y + h * 0.33, body, ha="center", va="center", fontsize=bfs, color=bc, linespacing=1.3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color=tc,
                linespacing=1.15)


def arrow(ax, p0, p1, color=INK, lw=0.9, ms=9):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def fig1_architecture():
    from fig1_power_path import render
    render(os.path.join(OUT, "fig1_architecture.png"), DPI)


def fig2_energy_budget():
    from simulation.energy_chain import I_SGP30, T_SGP30_ON, I_LIGHT
    e_sgp_warm = (I_SGP30 * V_CC * T_SGP30_ON + I_LIGHT * V_CC * (T_SGP30_ON - 1.0)) * 1e3
    items = ["SGP30, measurement only (50 ms)", "LoRa TX SF7 (41 ms)", "Deep sleep (per cycle)",
             "Base sensors (2 s)", "ESP32 active (2 s)", "SGP30 incl. 15 s warm-up", "MQ-135 stress (30 s heater)"]
    energy_mj = [7.9, 16.3, 19.8, 109.0, 528.0, e_sgp_warm, 22500.0]
    colors = [GREY] * 7; colors[4] = BLUE
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    y = np.arange(len(items))
    ax.barh(y, energy_mj, height=0.62, color=colors)
    ax.set_xscale("log"); grid(ax, "x")
    ax.axvline(90, color=INK, ls="--", lw=0.9)
    ax.text(90 * 1.1, 6.62, "harvested per 10-min cycle at 150 µW (90 mJ)", fontsize=6.8, color=INK, va="center")
    ax.set_yticks(y); ax.set_yticklabels(items)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Energy per event (mJ, log scale)")
    for yi, e in zip(y, energy_mj):
        lab = f"{e/1000:.1f} J" if e >= 1000 else f"{e:.0f} mJ"
        ax.text(e * 1.15, yi, lab, va="center", fontsize=7, color=INK2)
    ax.set_xlim(3, 90000); ax.set_ylim(-0.6, 7.0)
    save(fig, "fig2_energy_budget.png")


def fig3_interval():
    P = np.linspace(35, 500, 300)
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    ax.axvspan(15, 30, color=GREY, alpha=0.55, lw=0)
    for case in ("ideal", "realistic", "conservative"):
        dt = np.array([interval_h("lean", p * 1e-6, case) for p in P])
        dt[~np.isfinite(dt)] = np.nan
        ax.plot(P, dt, label=case, **CASE[case])
    ax.axvline(33, color=DGREY, ls="--", lw=0.8)
    ax.axvline(49.5, color=BLUE, ls=":", lw=1.0)
    ax.axvline(150, color=MUTE, ls=":", lw=0.9)
    ax.axhline(0.1667, color=INK2, ls="--", lw=0.8)
    ax.text(515, 0.183, "10-min target", fontsize=6.6, color=INK2, ha="right", va="bottom")
    ax.text(22.5, 0.24, "single cell 15–30 µW [14]", fontsize=6.2, color=INK2, rotation=90, va="bottom", ha="center")
    ax.text(34.5, 0.24, "ideal floor 33 µW", fontsize=6.2, color=DGREY, rotation=90, va="bottom")
    ax.text(51.0, 0.24, "realistic floor ~50 µW", fontsize=6.2, color=BLUE, rotation=90, va="bottom")
    ax.annotate("150 µW multi-cell target", xy=(150, interval_h("lean", 150e-6, "realistic")), xytext=(205, 9),
                fontsize=7, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    ax.set_xlabel("Mean MFC power at PMIC input (µW)"); ax.set_ylabel("Min. sustainable lean interval (h)")
    ax.set_yscale("log"); ax.set_ylim(0.1, 100); ax.set_xlim(10, 520); grid(ax)
    ax.legend(title="power path", title_fontsize=7, loc="upper right")
    save(fig, "fig3_interval.png")


def fig10_relations():
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.4))
    S = np.linspace(0.1, 3.0, 200)
    ocv = 0.85 + (8.314 * 298 / (2 * 96485)) * np.log(S)
    a = axs[0, 0]
    a.plot(S, ocv, color=BLUE, lw=1.8)
    a.axhline(0.855, color=MUTE, ls=":", lw=0.9)
    a.set_xlabel("Substrate [S] (g/L)"); a.set_ylabel("OCV (V)"); a.set_title("(a) Nernst OCV, Eq. (1)")
    R = np.linspace(50, 500, 200); ocv0 = 0.855
    Pm = ocv0 ** 2 / (4 * R) * 1e6
    a = axs[0, 1]
    a.plot(R, Pm, color=BLUE, lw=1.8)
    a.axvline(150, color=MUTE, ls=":", lw=0.9)
    a.set_xlabel("Internal resistance R_int (Ω)"); a.set_ylabel("Matched-load power (µW)")
    a.set_title("(b) Cell power, Eq. (2)")
    E_lean = e_event("lean")
    dt = np.linspace(0.5, 12, 200) * 3600
    a = axs[1, 0]
    for case in ("ideal", "realistic", "conservative"):
        a.plot(dt / 3600, p_net(150e-6, case) * dt / E_lean, label=case, **CASE[case])
    a.axhline(1.0, color=INK2, ls="--", lw=0.8)
    a.text(11.8, 1.15, "M = 1", fontsize=6.6, color=INK2, ha="right", va="bottom")
    a.set_xlabel("Reporting interval Δt (h)"); a.set_ylabel("Energy-positive margin M")
    a.set_title("(c) Margin, Eq. (12)"); a.legend(title="power path @150 µW", title_fontsize=6.6, fontsize=6.6)
    E = np.logspace(np.log10(0.1), np.log10(30), 200); Cmin = 2 * E / (0.90 * (5.0 ** 2 - 3.5 ** 2))
    a = axs[1, 1]
    a.plot(E, Cmin, color=BLUE, lw=1.8)
    a.axvline(0.653, color=INK2, ls="--", lw=0.8)
    a.axvline(24.1, color=INK2, ls="--", lw=0.8)
    a.text(0.653 * 1.12, 4.4, "lean 0.65 J", fontsize=6.6, color=INK2, va="top")
    a.text(24.1 / 1.12, 4.4, "MQ-135 stress 24 J", fontsize=6.6, color=INK2, va="top", ha="right")
    a.set_xscale("log"); a.set_ylim(0, 4.6)
    a.set_xlabel("Event energy E_event (J)"); a.set_ylabel("Min. capacitance C (F)")
    a.set_title("(d) Supercap sizing, Eq. (9)")
    for a in axs.flat:
        grid(a)
    fig.tight_layout(h_pad=1.6, w_pad=1.6)
    save(fig, "fig10_relations.png")


def fig4_lora():
    sf = ["SF7", "SF8", "SF9", "SF10", "SF11", "SF12"]
    toa = [41.2, 72.2, 144.4, 288.8, 577.5, 905.2]
    e_uj = [16.3, 28.6, 57.2, 114.4, 228.7, 358.5]
    colors = [BLUE] + [GREY] * 5
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for a, vals, ylab, title, fmt in ((a1, toa, "Time-on-air (ms)", "(a) Time-on-air, 13-byte payload", "{:.0f}"),
                                      (a2, e_uj, "TX energy per packet (mJ)", "(b) Transmit energy per packet", "{:.1f}")):
        a.bar(sf, vals, width=0.66, color=colors)
        for i, v in enumerate(vals):
            a.text(i, v + max(vals) * 0.02, fmt.format(v), ha="center", fontsize=6.6, color=INK2)
        a.set_ylabel(ylab); a.set_title(title); a.tick_params(axis="x", length=0)
        a.set_ylim(0, max(vals) * 1.12); grid(a)
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig4_lora.png")


def fig5_anomaly():
    classes = ["Drought", "pH crash", "Gas spike", "Flood"]
    recall = [1.00, 0.96, 1.00, 0.86]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    bars = a1.bar(classes, recall, width=0.62, color=[BLUE if r >= 0.9 else GREY for r in recall])
    a1.axhline(0.90, color=INK2, ls="--", lw=0.8)
    a1.text(3.45, 0.92, "0.90 target", fontsize=6.6, color=INK2, ha="right", va="bottom")
    a1.set_ylim(0, 1.1); a1.set_ylabel("Per-class recall"); a1.set_title("(a) Detection recall by anomaly type")
    for b, r in zip(bars, recall):
        a1.text(b.get_x() + b.get_width() / 2, r + 0.02, f"{r:.2f}", ha="center", fontsize=6.8, color=INK2)
    cond = ["Extreme\n(clean)", "Subtle\n(fixed thr.)", "Subtle\n(recalibrated)"]
    f1 = [0.963, 0.538, 0.880]; auc = [0.999, 0.929, 0.929]
    x = np.arange(len(cond)); w = 0.36
    a2.bar(x - w / 2, f1, w, label="F1", color=BLUE)
    a2.bar(x + w / 2, auc, w, label="ROC-AUC", color=GREY)
    a2.set_xticks(x); a2.set_xticklabels(cond); a2.set_ylim(0, 1.15)
    a2.set_ylabel("Score"); a2.set_title("(b) Synthetic upper bound vs shifted regime"); a2.legend(ncol=2, loc="upper right")
    for a in (a1, a2):
        a.tick_params(axis="x", length=0); grid(a)
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig5_anomaly.png")


def fig6_anchor():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9))
    s1 = ["Zheng\net al.", "Zhang\net al.", "Yen\net al.", "This\nmodel"]
    ocv = [0.733, 0.75, 0.731, 0.86]
    a1.axhspan(0.4, 0.8, color=RULE, lw=0)
    a1.text(-0.42, 0.41, "measured field range", fontsize=6.4, color=INK2, va="bottom")
    a1.bar(s1, ocv, width=0.6, color=[GREY, GREY, GREY, BLUE])
    a1.set_ylabel("Open-circuit voltage (V)"); a1.set_title("(a) OCV: model above measured")
    a1.set_ylim(0, 1.0)
    for i, v in enumerate(ocv):
        a1.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=6.8, color=INK2)
    s2 = ["Zhang\net al.", "Yang\net al.", "Yen\net al.", "This model\n(per cell)"]
    pdv = [3.0, 4.3, 11.5, 2.2]
    a2.bar(s2, pdv, width=0.6, color=[GREY, GREY, GREY, BLUE])
    a2.errorbar([2, 3], [11.5, 2.2], yerr=[[5.5, 0.7], [5.5, 0.8]], fmt="none", ecolor=INK, elinewidth=0.8, capsize=3)
    a2.set_ylabel("Power density (mW/m²)"); a2.set_title("(b) Power density: model per cell at low end")
    a2.set_ylim(0, 19)
    tops = {2: (17.0, "6–17"), 3: (3.0, "1.5–3.0")}
    for i, v in enumerate(pdv):
        y, lab = tops.get(i, (v, f"{v:g}"))
        a2.text(i, y + 0.3, lab, ha="center", fontsize=6.8, color=INK2)
    for a in (a1, a2):
        a.tick_params(axis="x", length=0)
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig6_anchor.png")


def fig7_supercap():
    C = 0.5; P = 150e-6; E_ev = 0.653 / 0.90
    Vmax, Vmin = 5.0, 3.5
    dt = 5.0; T = 6 * 3600
    n = int(T / dt)
    t = np.arange(n) * dt / 3600.0
    V = np.zeros(n); E = 0.5 * C * 3.6 ** 2
    P_bank = 0.80 / 0.90 * P - 33e-6 / 0.90 - 1.6e-6 - 5e-6
    interval_s = 2.26 * 3600
    next_ev = interval_s
    events = []
    for i in range(n):
        E = min(E + P_bank * dt, 0.5 * C * Vmax ** 2)
        if i * dt >= next_ev and E >= E_ev:
            E -= E_ev; events.append(i * dt / 3600.0); next_ev += interval_s
        V[i] = np.sqrt(2 * E / C)
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    for e in events:
        ax.axvline(e, color=RULE, lw=0.9, zorder=0)
    ax.plot(t, V, color=BLUE, lw=1.4)
    ax.axhline(Vmax, color=INK2, ls="--", lw=0.8)
    ax.axhline(Vmin, color=INK, ls="--", lw=0.8)
    ax.text(0.05, Vmax + 0.03, "V_max 5.0 V", fontsize=6.6, color=INK2, va="bottom")
    ax.text(0.05, Vmin + 0.03, "buck-dropout floor 3.5 V", fontsize=6.6, color=INK, va="bottom")
    if events:
        ax.text(events[0] + 0.06, 5.12, "lean event", fontsize=6.4, color=INK2, va="center")
    ax.set_xlabel("Time (h)"); ax.set_ylabel("Storage-bank voltage (V)")
    ax.set_ylim(3.3, 5.2); ax.set_xlim(0, 6)
    save(fig, "fig7_supercap.png")


def fig8_harvest_consume():
    cases = ["ideal", "realistic", "conservative"]
    net_j = [p_net(150e-6, c) * 86400 for c in cases]
    demand = 144 * e_event("lean")
    labels = [f"{c.capitalize()} net" for c in cases] + ["10-min lean demand"]
    vals = net_j + [demand]
    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    y = np.arange(4)[::-1]
    ax.barh(y, vals, height=0.6, color=[GREY, BLUE, DGREY, INK])
    for yi, v in zip(y[:3], net_j):
        ax.text(v + 1.2, yi, f"{v:.1f} J  ({demand / v:.1f}× short of demand)", va="center", fontsize=7, color=INK2)
    ax.text(demand - 1.2, y[3], f"{demand:.0f} J/day", va="center", ha="right", fontsize=7, color="white",
            fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Energy per day at 150 µW, lean payload (J/day)"); ax.set_xlim(0, demand * 1.03)
    grid(ax, "x")
    save(fig, "fig8_harvest_consume.png")


def fig9_sensitivity():
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.4))
    E_lean = e_event("lean"); base = interval_h("lean", 150e-6, "realistic")

    def dt_from(pmfc=150e-6, escale=1.0, eta=0.80, pleak=5e-6):
        pn = eta * pmfc - P_FLOOR - 1.6e-6 - pleak
        return E_lean * escale / pn / 3600 if pn > 0 else np.nan
    rows = [("Harvested P ±20%", dt_from(pmfc=180e-6), dt_from(pmfc=120e-6)),
            ("Active-wake ±30%", dt_from(escale=0.76), dt_from(escale=1.24)),
            ("PMIC eff. 0.72–0.88", dt_from(eta=0.88), dt_from(eta=0.72)),
            ("Leakage 1–15 µW", dt_from(pleak=1e-6), dt_from(pleak=15e-6))]
    rows = sorted(rows, key=lambda r: abs(r[2] - r[1]))
    y = np.arange(len(rows))
    a = axs[0, 0]
    for yi, (nm, lo, hi) in zip(y, rows):
        a.barh(yi, hi - lo, left=min(lo, hi), height=0.6, color=GREY)
    a.axvline(base, color=BLUE, ls="--", lw=1.0)
    a.text(base + 0.04, len(rows) - 0.45, f"baseline {base:.2f} h", fontsize=6.6, color=BLUE, va="bottom")
    a.set_yticks(y); a.set_yticklabels([r[0] for r in rows]); a.tick_params(axis="y", length=0)
    a.set_ylim(-0.6, len(rows) - 0.1)
    a.set_xlim(min(min(r[1], r[2]) for r in rows) - 0.12, max(max(r[1], r[2]) for r in rows) + 0.12)
    a.set_xlabel("Realistic lean interval Δt (h)"); a.set_title("(a) Tornado: Δt sensitivity"); grid(a, "x")
    dt = mc_interval("lean", 150e-6, n=20000)
    lo, hi = np.percentile(dt, 5), np.percentile(dt, 95)
    a = axs[0, 1]
    a.axvspan(lo, hi, color=RULE, lw=0)
    a.hist(dt, bins=50, density=True, range=(0, 6), color=LBLUE, edgecolor="white", linewidth=0.3)
    try:
        from scipy.stats import gaussian_kde
        xs = np.linspace(0, 6, 250); a.plot(xs, gaussian_kde(dt)(xs), color=BLUE, lw=1.5)
    except Exception:
        pass
    med = np.median(dt)
    a.axvline(med, color=INK, lw=1.0)
    a.axvline(2.0, color=MUTE, ls=":", lw=0.9)
    ytop = a.get_ylim()[1]
    a.text(med + 0.08, ytop * 0.93, f"median {med:.2f} h", fontsize=6.6, color=INK, va="top")
    a.text(hi - 0.06, ytop * 0.70, f"5–95%\n[{lo:.2f}, {hi:.2f}] h", fontsize=6.4, color=INK2, va="top", ha="right")
    a.set_xlim(0, 6); a.set_xlabel("Realistic lean interval Δt (h)"); a.set_ylabel("Probability density")
    a.set_title("(b) Monte Carlo (N=20000)")
    labs = ["Lean", "SGP30\n50 ms only", "SGP30 incl.\n15 s warm-up", "MQ-135\nstress"]
    ivs = [interval_h(p, 150e-6, "realistic") for p in ("lean", "lowgas", "sgp30", "mq135")]
    a = axs[1, 0]
    a.bar(labs, ivs, width=0.6, color=[BLUE, GREY, GREY, DGREY])
    a.set_yscale("log"); a.set_ylabel("Realistic interval (h)"); a.set_ylim(1, 300)
    a.set_title("(c) Payload cost (realistic)"); a.tick_params(axis="x", length=0); grid(a)
    for i, v in enumerate(ivs):
        a.text(i, v * 1.2, f"{v:.1f} h", ha="center", fontsize=6.8, color=INK2)
    esr = np.linspace(0, 20, 120); vt = 5.0 - I_TX * esr
    a = axs[1, 1]
    a.plot(esr, vt, color=BLUE, lw=1.8)
    a.axhline(3.5, color=INK, ls="--", lw=0.8)
    a.axvline(12.5, color=MUTE, ls=":", lw=1.0)
    a.text(0.3, 3.53, "3.5 V buck-dropout floor", fontsize=6.6, color=INK, va="bottom")
    a.text(12.9, 4.55, "R_ESR,max ≈ 12.5 Ω", fontsize=6.4, color=INK2, rotation=90, va="center")
    a.text(3.0, 4.72, "terminal V from 5.0 V", fontsize=6.6, color=BLUE, rotation=-14, va="bottom")
    a.set_xlabel("Series ESR (Ω)"); a.set_ylabel("Storage terminal voltage (V)"); a.set_ylim(2.8, 5.1)
    a.set_title("(d) LoRa-burst voltage sag (Eq. 10)"); grid(a)
    fig.tight_layout(h_pad=1.6, w_pad=1.6)
    save(fig, "fig9_sensitivity.png")


def fig_optim():
    Pn = p_net(150e-6, "realistic")
    El = e_event("lean"); Ef = e_event("mq135")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    f = np.linspace(0, 1, 200)
    total = Pn / ((1 - f) * El + f * Ef) * 86400
    a1.plot(total, f * total, color=BLUE, lw=1.8)
    for fv in [0.0, 0.05, 0.10, 0.25, 1.0]:
        tr = Pn / ((1 - fv) * El + fv * Ef) * 86400
        a1.plot(tr, fv * tr, "o", color=INK, ms=4)
        a1.annotate(f"f = {fv:.2f}", (tr, fv * tr), fontsize=6.4, color=INK2, xytext=(4, 3), textcoords="offset points")
    a1.set_xlabel("Total reports / day"); a1.set_ylabel("MQ-135 stress readings / day")
    a1.set_title("(a) Pareto: resolution vs gas coverage"); grid(a1)
    Ps = 22e-6; eta_stack = 0.75; eta_pmic = 0.80; pq = 1.6e-6; pleak = 5e-6
    dts = np.array([12, 6, 3, 1, 0.5, 1/6])
    Preq = P_FLOOR + El / (dts * 3600) + pq + pleak
    Ncells = np.ceil(Preq / (eta_pmic * eta_stack * Ps)).astype(int)
    a2.plot(dts, Ncells, "-", color=BLUE, lw=1.6)
    a2.plot(dts, Ncells, "s", color=INK, ms=4)
    for x, n in zip(dts, Ncells):
        a2.annotate(str(n), (x, n), fontsize=6.6, color=INK2, xytext=(-6, 5), textcoords="offset points", ha="right")
    a2.set_xscale("log"); a2.set_xlabel("Target reporting interval (h)"); a2.set_ylabel("Cells required N*")
    a2.set_title("(b) Min. cells (loss-aware)"); a2.invert_xaxis(); grid(a2)
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig_optim.png")


def fig_comm():
    fig, ax = plt.subplots(figsize=(7.3, 2.3))
    ax.axis("off"); ax.set_xlim(0, 12.85); ax.set_ylim(0.1, 3.7)
    stages = [("Sensor node", "ESP32 + sensors\n13-byte packet"),
              ("LoRa Tx", "Ra-02 433 MHz\nSF7, ToA (Eq. 4)"),
              ("Gateway", "ESP32 + WiFi\nLoRa Rx"),
              ("MQTT broker", "Mosquitto"),
              ("Cloud", "dashboard")]
    w, g, x = 2.06, 0.55, 0.15
    xs = []
    for i, (t, s) in enumerate(stages):
        dbox(ax, x, 1.15, w, 1.45, t, s)
        xs.append(x)
        if i < len(stages) - 1:
            arrow(ax, (x + w, 1.875), (x + w + g, 1.875))
        x += w + g
    bx0, bx1 = xs[0] - 0.1, xs[1] + w + 0.1
    ax.add_patch(Rectangle((bx0, 0.95), bx1 - bx0, 2.25, fill=False, ec=MUTE, lw=0.8, ls=(0, (3, 2))))
    ax.text(bx0 + 0.05, 3.27, "battery-free node budget", fontsize=6.6, color=INK2, va="bottom")
    ax.text(xs[1] + w / 2, 2.9, "16.3 mJ / packet", fontsize=7, color=BLUE, fontweight="bold", va="center",
            ha="center")
    ax.text(xs[2] + w / 2, 0.98, "externally powered", ha="center", va="top", fontsize=6.4, color=INK2, style="italic")
    ax.text(6.3, 0.32, "E_tx = I_tx · V_cc · ToA     SF7: 41.2 ms, 16.3 mJ     SF12: 905 ms, 358 mJ",
            ha="center", fontsize=7, color=INK2)
    save(fig, "fig_comm.png")


def fig_methods(include_rf=True):
    ncol = 4 if include_rf else 3
    fig, axs = plt.subplots(1, ncol, figsize=(7.4 if include_rf else 5.8, 3.3))

    def flow(ax, title, steps, math, primary):
        ec, tc = (INK, INK) if primary else (MUTE, INK2)
        ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 12)
        ax.text(5, 10.6, title, ha="center", fontsize=8, fontweight="bold", color=tc)
        y = 9.9; h = 1.45
        for i, st in enumerate(steps):
            ax.add_patch(Rectangle((1, y - h), 8, h, fill=False, ec=ec, lw=0.9))
            ax.text(5, y - h / 2, st, ha="center", va="center", fontsize=6.6, color=tc)
            if i < len(steps) - 1:
                arrow(ax, (5, y - h), (5, y - h - 0.55), color=ec, ms=8)
            y -= (h + 0.55)
        ax.text(5, 1.3, math, ha="center", va="center", fontsize=6.4, color=BLUE if primary else INK2, style="italic")
    flow(axs[0], "Monte Carlo", ["sample x ~ f(x)", "run energy model", "collect Δt(k)", "5–95% band"],
         "Δt(k) = E_event / P_net(k)", True)
    flow(axs[1], "Sobol", ["matrices A, B", "run model", "variance decomp.", "$S_1$, $S_T$"],
         "$S_1$ = Var[E(Y|x_i)] / Var(Y)", True)
    flow(axs[2], "Isolation Forest", ["random splits", "isolate sample", "path length h(x)", "anomaly score"],
         "s(x,ψ) = 2^(−E[h(x)]/c(ψ))", False)
    if include_rf:
        flow(axs[3], "Random Forest", ["rule labels", "fit B trees", "majority vote", "OTA update"],
             "ŷ = mode{T_b(x)}", False)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    split = 0.505 if include_rf else 0.672
    fig.text(split / 2, 0.955, "Primary analytical methods", ha="center", fontsize=7.4, fontweight="bold", color=INK)
    fig.text((1 + split) / 2, 0.955, "Secondary AI (illustrative)", ha="center", fontsize=7.4, color=INK2)
    fig.add_artist(plt.Line2D([split, split], [0.04, 0.95], transform=fig.transFigure, color=RULE, lw=1.0))
    save(fig, "fig_methods.png" if include_rf else "fig_methods_no_rf.png")


def fig_pipeline():
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0.1, 3.6)
    blocks = [("MFC harvester", "soil cell\n15–30 µW", "n"),
              ("Power model", "Nernst OCV\n(Eqs. 1–2)", "n"),
              ("Loss-aware PMIC", "η_PMIC, leakage\n(Eq. 6)", "key"),
              ("Energy budget", "per-event E\n(Eq. 3)", "n"),
              ("Supercapacitor", "buffer + ESR\n(Eqs. 9–11)", "n"),
              ("Duty-cycle core", "interval, margin\n(Eqs. 5–7, 12)", "n"),
              ("AI decision layer", "Isolation Forest\n(secondary)", "sec"),
              ("LoRa uplink", "SF7 ToA\n(Eq. 4)", "n")]
    cols = [1.55, 4.5, 7.45, 10.4]; w, h = 2.3, 1.15
    top_y, bot_y = 2.55, 0.85
    order = [(cols[i], top_y) for i in range(4)] + [(cols[3 - i], bot_y) for i in range(4)]
    for (t, s, kind), (cx, cy) in zip(blocks, order):
        ec, tc, lw = {"n": (INK, INK, 0.9), "key": (BLUE, BLUE, 1.6), "sec": (MUTE, INK2, 0.9)}[kind]
        dbox(ax, cx - w / 2, cy - h / 2, w, h, t, s, ec=ec, tc=tc, lw=lw, tfs=7.4, bfs=6.3)
    for i in range(3):
        arrow(ax, (cols[i] + w / 2, top_y), (cols[i + 1] - w / 2, top_y))
    arrow(ax, (cols[3], top_y - h / 2), (cols[3], bot_y + h / 2))
    for i in range(3):
        arrow(ax, (cols[3 - i] - w / 2, bot_y), (cols[3 - i - 1] + w / 2, bot_y))
    ax.text(cols[2], top_y + h / 2 + 0.12, "principal addition of this work", ha="center", va="bottom",
            fontsize=6.4, color=BLUE, style="italic")
    save(fig, "fig_pipeline.png")


def fig_dynamic():
    t, p, v, events, e_min, e_max = dynamic_scenario()
    th = t / 3600.0
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.7]})
    a1.plot(th, p * 1e6, color=INK2, lw=1.3)
    a1.axhline(150, color=MUTE, ls=":", lw=0.9)
    a1.text(71.5, 152, "daily mean 150 µW", fontsize=6.6, color=INK2, ha="right", va="bottom")
    a1.set_ylabel("Harvested power (µW)"); a1.set_ylim(100, 200); grid(a1)
    a2.plot(th, v, color=DGREY, lw=0.9, zorder=1)
    a2.axhline(5.0, color=INK2, ls="--", lw=0.8)
    a2.axhline(3.5, color=INK, ls="--", lw=0.8)
    a2.text(71.5, 5.02, "V_max 5.0 V", fontsize=6.4, color=INK2, ha="right", va="bottom")
    a2.text(71.5, 3.52, "buck-dropout floor 3.5 V", fontsize=6.4, color=INK, ha="right", va="bottom")
    for frac, lab in [(0.25, "SoC 0.25 (sleep below)"), (0.55, "SoC 0.55 (measure below)")]:
        vth = np.sqrt(2 * (e_min + frac * (e_max - e_min)) / 0.5)
        a2.axhline(vth, color=MUTE, ls=":", lw=0.8)
        a2.text(th[0] + 0.5, vth + 0.01, lab, fontsize=5.8, color=INK2, ha="left", va="bottom")
    mk = [("transmit", dict(marker="o", s=20, c=BLUE), "transmit"),
          ("measure", dict(marker="o", s=20, facecolors="white", edgecolors=INK, linewidths=0.8), "measure (store)"),
          ("sleep", dict(marker="x", s=24, c=INK, linewidths=1.0), "sleep (recharge)"),
          ("anomaly", dict(marker="*", s=70, c=INK), "anomaly override")]
    for key, kw, lab in mk:
        pts = [(tt / 3600.0, vb) for tt, a, vb, va in events if a == key]
        if pts:
            xs, ys = zip(*pts)
            a2.scatter(xs, ys, zorder=3, label=lab, **kw)
    a2.set_xlabel("Time (h)"); a2.set_ylabel("Storage-bank voltage (V)")
    a2.legend(fontsize=6.6, loc="upper center", ncol=4, handletextpad=0.3, columnspacing=1.2)
    a2.set_ylim(3.3, 5.55); a2.set_xlim(0, 72); grid(a2)
    fig.tight_layout(h_pad=0.8)
    save(fig, "fig_dynamic.png")


def fig_flowchart():
    fig, ax = plt.subplots(figsize=(6.4, 6.9))
    ax.axis("off"); ax.set_xlim(0.6, 10); ax.set_ylim(1.1, 12.9)

    def proc(x, y, w, h, txt, rounded=False, bold=False, ec=INK, tc=INK):
        st = "round,pad=0.02,rounding_size=0.35" if rounded else "square,pad=0.0"
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=st, lw=0.9, ec=ec, fc="white"))
        ax.text(x, y, txt, ha="center", va="center", fontsize=7.6, color=tc, fontweight="bold" if bold else "normal",
                linespacing=1.25)

    def dec(x, y, w, h, txt):
        ax.add_patch(Polygon([[x, y + h / 2], [x + w / 2, y], [x, y - h / 2], [x - w / 2, y]],
                             closed=True, lw=0.9, ec=INK, fc="white"))
        ax.text(x, y, txt, ha="center", va="center", fontsize=7.2, color=INK, linespacing=1.2)

    def arr(x0, y0, x1, y1, txt=""):
        arrow(ax, (x0, y0), (x1, y1), color=INK, ms=9)
        if txt:
            ax.text((x0 + x1) / 2 + 0.15, (y0 + y1) / 2 + 0.08, txt, fontsize=6.8, color=INK2, ha="left", va="bottom")
    ln = lambda x0, y0, x1, y1: ax.plot([x0, x1], [y0, y1], color=INK, lw=0.9, zorder=0, solid_capstyle="butt")
    proc(4, 12.3, 3.4, 0.75, "Wake from deep sleep", rounded=True)
    proc(4, 11.05, 3.6, 0.75, "Read SoC (one ADC conversion)")
    dec(4, 9.7, 3.0, 1.2, "SoC < 0.25 ?")
    proc(4, 8.3, 4.6, 0.9, "Read sensors;\ncompute anomaly score (IF)")
    dec(4, 6.75, 3.4, 1.3, "anomaly and\nSoC > 0.35 ?")
    dec(4, 4.85, 3.0, 1.2, "SoC < 0.55 ?")
    proc(4, 3.2, 2.4, 0.75, "TRANSMIT", bold=True, ec=BLUE, tc=BLUE)
    proc(8.3, 9.7, 1.9, 0.75, "SLEEP", bold=True)
    proc(8.3, 6.75, 1.9, 0.8, "TRANSMIT\n(override)", bold=True, ec=BLUE, tc=BLUE)
    proc(8.3, 4.85, 1.9, 0.75, "MEASURE", bold=True)
    proc(4, 1.7, 4.4, 0.75, "Deep sleep for interval Δt (Eq. 8)", rounded=True)
    arr(4, 11.925, 4, 11.425); arr(4, 10.675, 4, 10.3)
    arr(4, 9.1, 4, 8.75); arr(5.5, 9.7, 7.35, 9.7, "yes")
    ax.text(4.25, 8.92, "no", fontsize=6.8, color=INK2, ha="left", va="center")
    arr(4, 7.85, 4, 7.4); arr(5.7, 6.75, 7.35, 6.75, "yes")
    arr(4, 6.1, 4, 5.45, "no"); arr(5.5, 4.85, 7.35, 4.85, "yes")
    arr(4, 4.25, 4, 3.575, "no")
    arr(4, 2.825, 4, 2.075)
    for yb in (9.7, 6.75, 4.85):
        ln(9.25, yb, 9.7, yb)
    ln(9.7, 9.7, 9.7, 1.7)
    arr(9.7, 1.7, 6.2, 1.7)
    ln(1.8, 1.7, 1.0, 1.7); ln(1.0, 1.7, 1.0, 12.3)
    arr(1.0, 12.3, 2.3, 12.3)
    ax.text(1.12, 12.4, "loop", fontsize=6.8, color=INK2, ha="left", va="bottom")
    ax.text(6.0, 11.05, "≈ 66 mJ, paid on every wake", fontsize=6.0, color=INK2, ha="left", va="center", style="italic")
    ax.text(6.5, 8.3, "score s:\nhigher = more\nanomalous", fontsize=6.0, color=INK2, ha="left", va="center",
            style="italic")
    ax.text(1.65, 6.0, "heuristic\nSoC\nthresholds", fontsize=6.0, color=INK2, ha="center", va="center", style="italic")
    ax.text(8.3, 4.35, "(store locally)", fontsize=6.2, color=INK2, ha="center", va="top", style="italic")
    save(fig, "fig_flowchart.png")


def graphical_abstract():
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5)

    def box(x, w, title, val, sub):
        ax.add_patch(Rectangle((x, 1.4), w, 2.2, fill=False, ec=INK, lw=1.0))
        ax.text(x + w / 2, 3.15, title, ha="center", va="center", fontsize=8.6, fontweight="bold", color=INK,
                linespacing=1.15)
        ax.text(x + w / 2, 2.35, val, ha="center", va="center", fontsize=10, fontweight="bold", color=BLUE)
        ax.text(x + w / 2, 1.8, sub, ha="center", va="center", fontsize=7, color=INK2)
    box(0.2, 2.7, "Soil MFC", "15–30 µW", "per cell"); arrow(ax, (2.9, 2.5), (3.4, 2.5), ms=11)
    box(3.4, 2.7, "Loss-aware\npower path", "80 µW net", "η_PMIC, leakage, ESR"); arrow(ax, (6.1, 2.5), (6.6, 2.5), ms=11)
    box(6.6, 2.7, "150 µW target", "≈ 10 cells", "range 6–17"); arrow(ax, (9.3, 2.5), (9.8, 2.5), ms=11)
    box(9.8, 2.0, "Lean cadence", "2.3 h", "realistic")
    ax.text(10.8, 1.25, "MQ-135 gas: 57–121 h", ha="center", va="top", fontsize=6.6, color=INK2, style="italic")
    ax.text(6, 0.45, "A single soil-MFC cell is insufficient; a ≈10-cell 150 µW array supports a ~2.3 h realistic "
            "lean cadence.", ha="center", va="center", fontsize=8.6, color=INK)
    ax.text(6, 4.5, "Reproducible Energy-Budget Framework for Battery-Free MFC-Powered AIoT Nodes",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color=INK)
    save(fig, "graphical_abstract.png")


def fig_trace():
    import json
    import pandas as pd
    from simulation.energy_chain import trace_scenario
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tr = pd.read_csv(os.path.join(root, "external", "yen_smfc_trace_5min.csv"))
    t_s, p = tr.t_s.values, tr.p_cell_W.values
    days = pd.Series(p * 1e6, index=pd.to_timedelta(t_s, unit="s")).resample("1D").mean()
    d = np.arange(len(days))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.1]})
    a1.axhspan(15, 30, color=GREY, alpha=0.55, lw=0)
    a1.plot(d, days.values, color=BLUE, lw=1.2)
    a1.text(1, 32, "15–30 µW assumed in this work", fontsize=6.4, color=INK2, va="bottom")
    a1.set_yscale("symlog", linthresh=1); a1.set_ylim(0, 400)
    a1.set_ylabel("Single-cell power,\ndaily mean (µW)"); grid(a1)
    for c, lk, col, ls, lab in ((0.5, None, BLUE, "-", "0.5 F bank"), (5.0, None, INK, "--", "5 F, leakage 5 µW"),
                                (5.0, 50e-6, MUTE, ":", "5 F, leakage 50 µW (scaled with C)")):
        r = trace_scenario(t_s, p, n_cells=10, c_eq=c, pleak=lk)
        on = pd.Series(r["on"].astype(float), index=days.index[0] + pd.to_timedelta(t_s, unit="s")).resample("1D").mean()
        a2.plot(d, on.values[:len(d)], color=col, lw=1.3 if c == 0.5 else 1.0, ls=ls, label=lab)
    a2.set_ylim(-0.05, 1.05); a2.set_ylabel("Fraction of day\nthe node is on"); a2.set_xlabel("Day of the 161-day trace")
    a2.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3); grid(a2)
    for a, lab in ((a1, "(a)"), (a2, "(b)")):
        a.text(-0.1, 1.02, lab, transform=a.transAxes, fontsize=8, fontweight="bold", va="bottom")
    fig.tight_layout(h_pad=0.6)
    save(fig, "fig_trace.png")


def fig_wake():
    t = np.array([0.1, 0.25, 0.5, 1.0, 2.0, 5.0])
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.axvspan(0.05, 0.3, color=GREY, alpha=0.55, lw=0)
    for case in ("ideal", "realistic", "conservative"):
        pn = p_net(150e-6, case)
        dt_min = np.array([(V_CC * (I_ACT + I_SENS) * ti + E_TX) / pn / 60.0 for ti in t])
        ax.plot(t, dt_min, marker="o", ms=3.5, label=case, **CASE[case])
    ax.axhline(10, color=INK2, ls="--", lw=0.8)
    ax.text(6.6, 10.8, "10-min target", fontsize=6.6, color=INK2, ha="right", va="bottom")
    ax.text(0.124, 150, "impractical\n(ESP32 boot +\nsensor settling)", fontsize=6.2, color=INK2, ha="center",
            va="center")
    ax.axvline(2.0, color=MUTE, ls=":", lw=0.9)
    ax.text(2.12, 12, "baseline 2 s", fontsize=6.4, color=INK2, rotation=90, va="bottom")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.05, 7)
    ax.set_xlabel("ESP32 active-wake duration t_active (s)")
    ax.set_ylabel("Sustainable lean interval (min)")
    ax.legend(title="power path", title_fontsize=7, loc="upper left", bbox_to_anchor=(0.18, 1.0)); grid(ax)
    fig.tight_layout()
    save(fig, "fig_wake.png")


def fig_uq_flow():
    fig, ax = plt.subplots(figsize=(7.6, 1.9))
    ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0.55, 2.45)
    boxes = [("Uncertain\nparameters", "P_MFC, η,\nP_leak, E_event"),
             ("Monte Carlo\nsampling", "N = 20,000\ndraws"),
             ("Loss-aware\nenergy model", "P_net\n(Eq. 6)"),
             ("Closed-form\noptimum", "r* = P_net / E_event\n(Eq. 7)"),
             ("Distribution of\nsustainable cadence", "median 2.45 h\n[1.42, 4.76]")]
    w = 2.15; gap = 0.35; x = 0.15
    for i, (t, sub) in enumerate(boxes):
        last = i == len(boxes) - 1
        dbox(ax, x, 0.7, w, 1.6, t, sub, ec=BLUE if last else INK, tc=BLUE if last else INK,
             bc=BLUE if last else INK2, lw=1.4 if last else 0.9, tfs=7.0, bfs=6.4)
        if not last:
            arrow(ax, (x + w, 1.5), (x + w + gap, 1.5))
        x += w + gap
    save(fig, "fig_uq_flow.png")


if __name__ == "__main__":
    graphical_abstract(); fig_flowchart(); fig_pipeline(); fig_dynamic(); fig_comm(); fig_methods(); fig_optim(); fig_methods(include_rf=False)
    fig1_architecture(); fig2_energy_budget(); fig3_interval()
    fig4_lora(); fig5_anomaly(); fig6_anchor()
    fig7_supercap(); fig8_harvest_consume(); fig9_sensitivity(); fig10_relations()
    fig_wake()
    fig_uq_flow()
    fig_trace()
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            print("wrote", os.path.join("figures", f))
