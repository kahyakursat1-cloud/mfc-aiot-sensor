"""
paper/fig1_power_path.py
Figure 1: (a) power-path schematic of the node, (b) daily energy flow at 150 uW
(realistic power path). All flow values come from simulation.energy_chain.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, PathPatch, FancyBboxPatch
from matplotlib.path import Path

from simulation.energy_chain import CASES, P_FLOOR, V_CC, I_ACT, I_SENS, E_TX, e_event

INK, INK2, MUTE = "#0b0b0b", "#52514e", "#a8a6a0"
BLUE, GREY = "#1e78d2", "#b9b7b0"
RC = {"font.family": "Arial", "font.size": 8, "axes.grid": False}


def line(ax, xs, ys, **k):
    ax.plot(xs, ys, color=k.pop("color", INK), lw=k.pop("lw", 1.0), solid_capstyle="round", **k)


def cell(ax, x, y, w=2.2):
    line(ax, [x - w / 2, x + w / 2], [y + 0.45, y + 0.45], lw=1.2)
    line(ax, [x - w / 4, x + w / 4], [y - 0.25, y - 0.25], lw=2.2)


def cap(ax, x, y, w=2.6):
    line(ax, [x - w / 2, x + w / 2], [y + 0.35, y + 0.35], lw=1.4)
    line(ax, [x - w / 2, x + w / 2], [y - 0.35, y - 0.35], lw=1.4)


def gnd(ax, x, y):
    for i, w in enumerate((2.0, 1.3, 0.6)):
        line(ax, [x - w / 2, x + w / 2], [y - 0.45 * i, y - 0.45 * i], lw=1.0)


def vdots(ax, x, y):
    ax.plot([x, x, x], [y - 0.9, y, y + 0.9], ls="none", marker="o", ms=1.6, color=INK)


def box(ax, x0, y0, x1, y1, title, body):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=INK, lw=1.0))
    ax.text((x0 + x1) / 2, y1 - 1.1, title, ha="center", va="top", fontsize=8, fontweight="bold", color=INK)
    ax.text((x0 + x1) / 2, y1 - 3.6, body, ha="center", va="top", fontsize=6.0, color=INK2, linespacing=1.35)


# ---------------------------------------------------------------- A. schematic
def draw_schematic(ax):
    ax.set_xlim(0, 100); ax.set_ylim(2.5, 38); ax.axis("off")
    GY = 5.5
    ax.add_patch(FancyBboxPatch((1.5, 9.0), 20, 24.5, boxstyle="round,pad=0.3", fill=False, ec=MUTE, lw=0.9, ls=(0, (3, 2))))
    ax.text(11.5, 35.6, "Soil-MFC array", ha="center", fontsize=8, fontweight="bold")
    ax.text(11.5, 32.2, "~10 cells, 15–30 µW each", ha="center", fontsize=5.9, color=INK2)
    for sx in (8.0, 15.0):
        for cy in (26.8, 22.8):
            cell(ax, sx, cy)
        vdots(ax, sx, 18.6)
        cell(ax, sx, 14.0)
        line(ax, [sx, sx], [29.5, 27.25]); line(ax, [sx, sx], [26.55, 23.25]); line(ax, [sx, sx], [22.55, 20.6])
        line(ax, [sx, sx], [16.6, 14.45]); line(ax, [sx, sx], [13.75, 11.0])
    line(ax, [8.0, 15.0], [29.5, 29.5]); line(ax, [8.0, 15.0], [11.0, 11.0])
    line(ax, [11.5, 11.5], [11.0, GY]); gnd(ax, 11.5, GY)
    line(ax, [15.0, 29.0], [29.5, 29.5])
    ax.text(25.3, 30.2, "150 µW", ha="center", va="bottom", fontsize=7, color=BLUE, fontweight="bold")
    ax.add_patch(Rectangle((29.0, 18.5), 19.5, 14.5, fill=False, ec=INK, lw=1.3))
    ax.text(38.75, 31.6, "BQ25570", ha="center", va="top", fontsize=8.5, fontweight="bold")
    ax.text(38.75, 28.4, "boost charger + buck", ha="center", va="top", fontsize=6.6, color=INK2)
    ax.text(38.75, 37.6, "MPPT, cold start ≥ 600 mV\nη ≈ 0.80, I_q = 488 nA", ha="center", va="top",
            fontsize=6.2, color=INK2, linespacing=1.3)
    ax.text(29.6, 29.5, "VIN", fontsize=5.6, va="center", color=MUTE)
    ax.text(47.9, 25.0, "VOUT", fontsize=5.6, va="center", ha="right", color=MUTE)
    ax.text(38.75, 19.3, "VSTOR", fontsize=5.6, ha="center", color=MUTE)
    line(ax, [38.75, 38.75], [18.5, 15.6]); cap(ax, 38.75, 15.25)
    line(ax, [38.75, 38.75], [14.9, 12.1]); cap(ax, 38.75, 11.75)
    line(ax, [38.75, 38.75], [11.4, GY]); gnd(ax, 38.75, GY)
    ax.text(36.6, 13.5, "2 × 2.7 V / 1 F\nin series = 0.5 F\n3.5–5.0 V, ≈ 3.2 J", fontsize=6.2, color=INK2,
            va="center", ha="right", linespacing=1.3)
    RY = 25.0
    line(ax, [48.5, 96.5], [RY, RY], lw=1.3)
    ax.text(49.5, RY + 0.7, "3.3 V regulated rail", fontsize=6.6, color=INK, va="bottom")
    ax.text(49.5, RY - 0.8, "P_net ≈ 80 µW", fontsize=7, color=BLUE, fontweight="bold", va="top")
    loads = [(55.5, 68.5, "ESP32", "sleep 10 µA\nwake 80 mA, 2 s"),
             (70.5, 81.5, "Sensors", "3 soil probes\n16.5 mA, 2 s"),
             (83.5, 94.0, "LoRa", "SF7, 120 mA\n16.3 mJ/pkt")]
    for x0, x1, t, b in loads:
        xm = (x0 + x1) / 2
        line(ax, [xm, xm], [RY, 19.5]); box(ax, x0, 9.5, x1, 19.5, t, b)
        line(ax, [xm, xm], [9.5, GY]); gnd(ax, xm, GY)
    line(ax, [96.5, 96.5], [RY, 17.8]); cap(ax, 96.5, 17.45, w=2.0)
    line(ax, [96.5, 96.5], [17.1, GY]); gnd(ax, 96.5, GY)
    ax.text(97.6, 14.2, "low-ESR\nburst cap", fontsize=5.8, color=INK2, va="center", linespacing=1.2)
    line(ax, [92.6, 92.6], [19.5, 21.6]); line(ax, [91.8, 92.6, 93.4], [22.4, 21.6, 22.4])
    ax.text(99.5, 37.6, "to gateway (mains-powered,\noutside the node budget)", ha="right", va="top",
            fontsize=6.2, color=INK2, style="italic", linespacing=1.25)
    ax.add_patch(FancyArrowPatch((93.6, 22.8), (96.0, 32.6), arrowstyle="-|>", mutation_scale=8,
                                 color=MUTE, lw=0.9, ls=(0, (3, 2))))


# ---------------------------------------------------------------- B. sankey
def link(ax, x0, y0b, y0t, x1, y1b, y1t, color, alpha=0.55):
    xm = (x0 + x1) / 2
    verts = [(x0, y0t), (xm, y0t), (xm, y1t), (x1, y1t), (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0t)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec="none", alpha=alpha))


def draw_sankey(ax, footer):
    c = CASES["realistic"]; day = 86400
    harvest = 150e-6 * day
    pmic = (1 - c["eta"]) * harvest
    floor = P_FLOOR * day; leak = c["pleak"] * day; quies = c["pq"] * day
    net = harvest - pmic - floor - leak - quies
    ev = e_event("lean"); n_ev = net / ev
    wake = V_CC * I_ACT * 2.0 * n_ev; sens = V_CC * I_SENS * 2.0 * n_ev; radio = E_TX * n_ev
    assert abs(wake + sens + radio - net) < 1e-6
    S, G, W = 1.0, 0.55, 1.3
    ax.set_xlim(-14, 112); ax.set_ylim(-3.2 if footer else -1.4, 16.2); ax.axis("off")
    x1, x2, x3 = 6, 46, 84
    col2 = [("Net available for events", net, BLUE), ("PMIC conversion (η = 0.80)", pmic, GREY),
            ("ESP32 deep-sleep floor (33 µW)", floor, GREY), ("Leakage + balancing (5 µW)", leak, GREY),
            ("PMIC quiescent (1.6 µW)", quies, GREY)]
    tot2 = sum(v for _, v, _ in col2) * S + G * (len(col2) - 1)
    top = 14.2; y = top; pos2 = []
    for name, v, colr in col2:
        h = v * S; pos2.append((name, v, colr, y - h, y)); y -= h + G
    h1 = harvest * S; s_top = top - (tot2 - h1) / 2; s_bot = s_top - h1
    ax.add_patch(Rectangle((x1 - W, s_bot), W, h1, fc=INK, ec="none"))
    ax.text(x1 - W - 1.2, (s_top + s_bot) / 2, f"Harvested\n{harvest:.2f} J/day\n(150 µW)", ha="right",
            va="center", fontsize=7.5, fontweight="bold", color=INK, linespacing=1.3)
    yc = s_top
    for name, v, colr, b, t in pos2:
        h = v * S
        link(ax, x1, yc - h, yc, x2 - W, b, t, colr); yc -= h
        ax.add_patch(Rectangle((x2 - W, b), W, t - b, fc=(BLUE if colr == BLUE else "#8d8b85"), ec="none"))
        if colr != BLUE:
            ax.text(x2 + 0.8, (b + t) / 2, f"{name}   {v:.2f} J", ha="left", va="center", fontsize=6.6, color=INK2)
    nb, nt = pos2[0][3], pos2[0][4]
    ax.text(x2 - W / 2, nt + 0.5, f"{net:.2f} J/day net", ha="center", va="bottom", fontsize=7.5,
            fontweight="bold", color=BLUE)
    col3 = [("ESP32 active wake", wake), ("Sensors", sens), ("LoRa packet (SF7)", radio)]
    tot3 = sum(v for _, v in col3) * S + G * 2
    y = (nt + nb) / 2 + tot3 / 2; yc = nt
    for name, v in col3:
        h = v * S
        link(ax, x2, yc - h, yc, x3 - W, y - h, y, BLUE, alpha=0.45)
        ax.add_patch(Rectangle((x3 - W, y - h), W, h, fc=BLUE, ec="none"))
        ax.text(x3 + 0.8, y - h / 2, f"{name}   {v:.2f} J  ({100 * v / net:.0f}%)", ha="left", va="center",
                fontsize=6.8, color=INK)
        yc -= h; y -= h + G
    ax.text(x3 - W, 4.6, f"{net:.2f} J ÷ {ev:.2f} J per lean event\n= {n_ev:.1f} reports/day, one every {24 / n_ev:.2f} h",
            ha="left", va="top", fontsize=7, color=INK, linespacing=1.35)
    if footer:
        ax.text(-14, -2.6, f"Daily energy flow of the node at 150 µW, realistic power path. Periodic 10-minute reporting "
                f"would need {144 * ev:.0f} J/day, {144 * ev / net:.1f}× the energy left for events.",
                fontsize=6.6, color=INK2, style="italic")


def render(path, dpi):
    with plt.rc_context(RC):
        fig = plt.figure(figsize=(7.2, 6.3))
        gs = fig.add_gridspec(2, 1, height_ratios=[3.1, 3.0], hspace=0.08)
        a, b = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
        draw_schematic(a); draw_sankey(b, footer=False)
        for ax, lab in ((a, "(a)"), (b, "(b)")):
            ax.text(0.0, 1.0, lab, transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")
        fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
