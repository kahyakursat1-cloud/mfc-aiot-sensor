"""
simulation/energy_chain.py
==========================
Single source of truth for the physically realistic energy-chain model of the
battery-free soil-MFC-powered AIoT node (Energies major-revision).

Extends the ideal budget Dt = E_event/(P_MFC - P_floor) with the real power-path:

    P_net = eta_PMIC * P_MFC - P_floor - P_PMIC_q - P_leak
    Dt    = E_event / P_net            (feasible iff P_net > 0)

Three operating cases are evaluated: ideal (no conversion/parasitic losses),
realistic (BQ25570 datasheet efficiency + quiescent + supercap leakage), and
conservative (low efficiency + high leakage). Also derives the 150 uW design
point from a probabilistic multi-cell stack, checks the supercapacitor ESR
voltage-sag constraint during LoRa transmit, runs a Monte Carlo with physically
appropriate distributions, and computes predicted-vs-measured cadence errors.

Datasheet anchors:
  BQ25570 (TI SLUSBH2): quiescent ~488 nA; cold-start >=600 mV (>=330 mV is BQ25504) / ~15 uW input;
    boost efficiency up to ~93 % peak, ~75-85 % at uW-level input.
  Supercapacitor (1 F/2.7 V class): ESR ~1-30 ohm; leakage ~1-10 uA.

Run:  python simulation/energy_chain.py
"""

import numpy as np

# ---- fixed electrical parameters (paper Table 2) ---------------------------
V_CC   = 3.3
I_ACT  = 80e-3
I_SENS = (5 + 1.5 + 10) * 1e-3          # moisture + temperature + pH
I_SLEEP = 10e-6
I_TX   = 120e-3
TOA    = 0.0412
E_TX   = I_TX * V_CC * TOA              # 16.3 mJ
P_FLOOR = I_SLEEP * V_CC               # 33 uW
# SGP30 (Sensirion datasheet v1.0, 2020): 48.8 mA in measurement mode, 15 s initialisation
# after sgp30_iaq_init before valid data; ESP32 light sleep (0.8 mA) while the sensor warms up.
I_SGP30 = 48.8e-3
T_SGP30_ON = 16.0
I_LIGHT = 0.8e-3
# A wake that only reads the state of charge before deciding to sleep (assumed 0.25 s at
# the active current: ESP32 boot from deep sleep plus one ADC conversion).
T_CHECK = 0.25
E_CHECK = V_CC * I_ACT * T_CHECK

# ---- per-event energies for the THREE payload classes ----------------------
def e_event(payload):
    """J per measure-and-transmit event."""
    if payload == "lean":                     # 3 sensors, 2 s active
        t = 2.0
        return V_CC * (I_ACT * t + I_SENS * t) + E_TX
    if payload == "lowgas":                   # + low-power gas (SGP30), 2 s
        t = 2.0
        e_gas = 48e-3 * V_CC * 0.012          # SGP30 ~48 mA, sgp30_measure_iaq 12 ms (max)
        return V_CC * (I_ACT * t + I_SENS * t) + e_gas + E_TX
    if payload == "sgp30":                    # SGP30 with its 15 s warm-up after each power-up
        t = 2.0
        e_gas = I_SGP30 * V_CC * T_SGP30_ON + I_LIGHT * V_CC * (T_SGP30_ON - 1.0)
        return V_CC * (I_ACT * t + I_SENS * t) + e_gas + E_TX
    if payload == "mq135":                    # MQ-135 STRESS case, datasheet heater, 5 s
        t = 5.0
        e_heater = 150e-3 * 5.0 * 30.0        # 150 mA @ 5 V rated heater, 30 s = 22.5 J
        return V_CC * (I_ACT * t + I_SENS * t) + e_heater + E_TX
    raise ValueError(payload)

# ---- power-path cases (eta_PMIC, P_PMIC_q, P_leak) --------------------------
CASES = {
    "ideal":        dict(eta=1.00, pq=0.0,     pleak=0.0),
    "realistic":    dict(eta=0.80, pq=1.6e-6,  pleak=5e-6),   # BQ25570 488 nA; ~2 uA leak
    "conservative": dict(eta=0.70, pq=1.6e-6,  pleak=15e-6),  # low eta, ~6 uA leak
}

def p_net(p_mfc, case):
    c = CASES[case]
    return c["eta"] * p_mfc - P_FLOOR - c["pq"] - c["pleak"]

def interval_h(payload, p_mfc, case):
    pn = p_net(p_mfc, case)
    if pn <= 0:
        return float("inf")
    return e_event(payload) / pn / 3600.0

# ---- supercapacitor ESR voltage-sag constraint -----------------------------
def esr_constraint(esr_ohm, v_start, v_min=3.5, i_peak=I_TX):
    """During a LoRa TX burst the storage-bank voltage sags by I_peak*ESR.
    Two series 2.7 V cells (0.5 F, 5.4 V); v_min = 3.5 V is the buck-dropout
    floor for the regulated 3.3 V rail. i_peak is a conservative upper bound
    (the exact bank current is I_tx*V_cc/(eta_buck*V_bank) <= I_tx).
    Feasible iff v_start - i_peak*esr >= v_min."""
    v_sag = i_peak * esr_ohm
    v_terminal = v_start - v_sag
    v_start_min = v_min + v_sag           # minimum charge voltage to survive the burst
    return dict(v_sag=v_sag, v_terminal=v_terminal, ok=v_terminal >= v_min,
                v_start_min=v_start_min)

# ---- 150 uW design point from a multi-cell stack ---------------------------
def cells_for_target(p_target=150e-6, p_single=22e-6, eta_stack=0.75):
    """P_array = N * P_single * eta_stack  ->  N = ceil(P_target/(P_single*eta_stack))."""
    return int(np.ceil(p_target / (p_single * eta_stack)))

def mc_cells(p_target=150e-6, n=20000, seed=1):
    rng = np.random.default_rng(seed)
    # P_single Lognormal with mean ~22 uW over field range 15-30 uW
    mu, sig = np.log(22e-6), 0.20
    p_single = np.clip(rng.lognormal(mu, sig, n), 10e-6, 40e-6)
    eta_stack = rng.uniform(0.65, 0.90, n)
    N = np.ceil(p_target / (p_single * eta_stack))
    return N

# ---- Monte Carlo of the realistic lean interval ----------------------------
def mc_interval(payload="lean", p_mfc_nom=150e-6, n=20000, seed=42, return_stats=False):
    rng = np.random.default_rng(seed)
    # physically appropriate distributions
    p_mfc = np.clip(rng.lognormal(np.log(p_mfc_nom), 0.20, n), 80e-6, 400e-6)
    t_act = np.clip(rng.triangular(1.5, 2.0, 3.0, n), 1.5, 3.0)
    eta   = (0.71 + 0.25 * rng.beta(5, 2, n)) * (0.86 + 0.07 * rng.beta(4, 3, n))   # eta_boost * eta_buck, mean 0.80, max 0.89
    pq    = np.clip(rng.lognormal(np.log(1.6e-6), 0.3, n), 0.5e-6, 5e-6)
    pleak = np.clip(rng.lognormal(np.log(5e-6), 0.5, n), 1e-6, 25e-6)
    floor = np.clip(rng.normal(33e-6, 3e-6, n), 25e-6, 40e-6)
    e_ev  = V_CC * (I_ACT * t_act + I_SENS * t_act) + E_TX
    pn    = eta * p_mfc - floor - pq - pleak
    n_infeasible = int(np.sum(pn <= 0))
    dt    = np.where(pn > 0, e_ev / pn / 3600.0, np.inf)
    dt    = dt[np.isfinite(dt)]
    if return_stats:
        return dt, n_infeasible, n
    return dt

# ---- external validation: predicted vs measured cadence --------------------
def ocv_mape(model_ocv=0.86, measured=(0.733, 0.75, 0.731)):
    """Clean quantitative validation: modelled OCV vs three independent measured
    values. This axis IS node-independent, so a MAPE is meaningful here."""
    errs = [abs(model_ocv - m) / m * 100.0 for m in measured]
    return float(np.mean(errs)), errs

def cadence_consistency():
    """Cadence is NOT reduced to a single MAPE because the deployments use
    different node classes (Zheng: nRF24; this model: ESP32). Instead we report
    the ideal-case ESP32-lean point prediction (isolating the energy accounting),
    the realistic-case boundary (which explains the node choice), and the range
    consistency."""
    zheng_ideal = interval_h("lean", 41e-6, "ideal")        # ESP32-lean, no losses
    zheng_real_pnet = p_net(41e-6, "realistic")             # <0 -> ESP32 infeasible
    return dict(
        zheng_ideal_h=zheng_ideal,
        zheng_ideal_err=abs(zheng_ideal - 23.0) / 23.0 * 100.0,
        zheng_realistic_pnet_uW=zheng_real_pnet * 1e6,
        zheng_realistic_feasible=zheng_real_pnet > 0,
    )


def sobol_lossaware(n=65536, seed=1):
    """First-order (S1) and total-order (ST) Sobol indices of the realistic lean
    reporting rate r* = P_net/E_event (reports/day, Eq. 11) over the six loss-aware
    parameters. The rate is used instead of the interval Dt = 1/r*, which is singular
    as P_net -> 0: a handful of near-infeasible draws then dominate Var(Dt) and the
    indices change by up to 0.1 between seeds. On r* they are seed-stable."""
    rng = np.random.default_rng(seed)
    def smp(k):
        return np.column_stack([
            np.clip(rng.lognormal(np.log(150e-6), 0.20, k), 80e-6, 400e-6),   # P_MFC
            np.clip(rng.triangular(1.5, 2.0, 3.0, k), 1.5, 3.0),              # t_active
            (0.71 + 0.25 * rng.beta(5, 2, k)) * (0.86 + 0.07 * rng.beta(4, 3, k)),   # eta_PMIC = eta_boost*eta_buck (mean 0.80)
            np.clip(rng.lognormal(np.log(5e-6), 0.5, k), 1e-6, 25e-6),        # P_leak
            np.clip(rng.normal(1.0, 0.15, k), 0.6, 1.4),                     # sensor mult
            np.clip(rng.normal(33e-6, 3e-6, k), 25e-6, 40e-6),               # floor
        ])
    def model(X):
        p, t, eta, leak, sm, fl = X.T
        e = V_CC * (I_ACT * t + I_SENS * t * sm) + E_TX
        return (eta * p - fl - 1.6e-6 - leak) / e * 86400.0
    A, B = smp(n), smp(n)
    yA, yB = model(A), model(B)
    VarY = np.var(np.concatenate([yA, yB]))
    names = ["Harvested power", "Active duration", "PMIC efficiency",
             "Supercap leakage", "Sensor current", "Sleep floor"]
    out = []
    for i in range(6):
        AB = A.copy(); AB[:, i] = B[:, i]
        yAB = model(AB)
        S1 = max(np.mean(yB * (yAB - yA)) / VarY, 0.0)
        ST = 0.5 * np.mean((yA - yAB) ** 2) / VarY
        out.append((names[i], S1, ST))
    return out


def sobol_ci(n=65536, n_boot=400, seed=1):
    """Sobol S1/ST of the lean reporting rate r* (see sobol_lossaware) with
    bootstrap 95% CIs from resampling the output vectors (yA, yB, yAB_i)."""
    rng = np.random.default_rng(seed)
    def smp(k):
        return np.column_stack([
            np.clip(rng.lognormal(np.log(150e-6), 0.20, k), 80e-6, 400e-6),
            np.clip(rng.triangular(1.5, 2.0, 3.0, k), 1.5, 3.0),
            (0.71 + 0.25 * rng.beta(5, 2, k)) * (0.86 + 0.07 * rng.beta(4, 3, k)),
            np.clip(rng.lognormal(np.log(5e-6), 0.5, k), 1e-6, 25e-6),
            np.clip(rng.normal(1.0, 0.15, k), 0.6, 1.4),
            np.clip(rng.normal(33e-6, 3e-6, k), 25e-6, 40e-6),
        ])
    def model(X):
        p, t, eta, leak, sm, fl = X.T
        e = V_CC * (I_ACT * t + I_SENS * t * sm) + E_TX
        return (eta * p - fl - 1.6e-6 - leak) / e * 86400.0
    A, B = smp(n), smp(n)
    yA, yB = model(A), model(B)
    yAB = []
    for i in range(6):
        AB = A.copy(); AB[:, i] = B[:, i]
        yAB.append(model(AB))
    names = ["Harvested power", "Active duration", "PMIC efficiency",
             "Supercap leakage", "Sensor current", "Sleep floor"]
    def s1_st(a, b, ab):
        vy = np.var(np.concatenate([a, b]))
        return (max(np.mean(b * (ab - a)) / vy, 0.0),
                0.5 * np.mean((a - ab) ** 2) / vy)
    out = []
    for i in range(6):
        s1, st = s1_st(yA, yB, yAB[i])
        bs1, bst = [], []
        for _ in range(n_boot):
            idx = rng.integers(0, n, n)
            b1, b2 = s1_st(yA[idx], yB[idx], yAB[i][idx])
            bs1.append(b1); bst.append(b2)
        out.append((names[i], s1, np.percentile(bs1, 2.5), np.percentile(bs1, 97.5),
                    st, np.percentile(bst, 2.5), np.percentile(bst, 97.5)))
    return out


ETA_BUCK = 0.90        # buck efficiency used to refer rail energy back to the bank


def bank_terms(case):
    """Bank-referenced split of the combined efficiency: eta_PMIC = eta_in * eta_buck.
    Harvest enters the bank at eta_in; rail loads (sleep floor, events, wake checks) leave it
    divided by eta_buck; PMIC quiescent draw and leakage act on the bank directly."""
    eb = 1.0 if case == "ideal" else ETA_BUCK
    return CASES[case]["eta"] / eb, eb


def dynamic_scenario(wake_h=1.9, soc0=0.8, anomalies_h=(28, 52), T_h=72, dt=60,
                     p0=150e-6, amp=0.2, case="realistic", c_eq=0.5, v_max=5.0, v_min=3.5):
    """Algorithm 2 under a diurnal harvest P(t) = P0 (1 + amp sin 2 pi t / 24 h), with
    bank-referenced energy accounting (bank_terms); SoC is the usable-energy fraction of the
    [v_min, v_max] window. An anomaly overrides only when SoC > 0.35; otherwise the wake falls
    through to the SoC rule and the anomaly stays pending. The state-of-charge check is part of
    the 2 s active window of a measuring wake and is paid on its own only by a SLEEP wake."""
    cs = CASES[case]
    eta_in, eb = bank_terms(case)
    e_min, e_max = 0.5 * c_eq * v_min ** 2, 0.5 * c_eq * v_max ** 2
    e_lean = e_event("lean") / eb; e_meas = (e_event("lean") - E_TX) / eb; e_chk = E_CHECK / eb
    t = np.arange(0, T_h * 3600, dt)
    p = p0 * (1 + amp * np.sin(2 * np.pi * t / 86400))
    pnet = eta_in * p - P_FLOOR / eb - cs["pq"] - cs["pleak"]
    E = e_min + soc0 * (e_max - e_min)
    nxt = wake_h * 3600
    pending = sorted(a * 3600 for a in anomalies_h)
    events = []
    v = np.empty(len(t))
    for i, ti in enumerate(t):
        E = min(E + pnet[i] * dt, e_max)
        if ti >= nxt:
            nxt += wake_h * 3600
            soc = (E - e_min) / (e_max - e_min)
            v_before = np.sqrt(2 * E / c_eq)
            if pending and pending[0] <= ti and soc > 0.35:
                E -= e_lean; action = "anomaly"; pending.pop(0)
            elif soc < 0.25:
                E -= e_chk; action = "sleep"
            elif soc < 0.55:
                E -= e_meas; action = "measure"
            else:
                E -= e_lean; action = "transmit"
            events.append((ti, action, v_before, np.sqrt(2 * E / c_eq)))
        v[i] = np.sqrt(2 * E / c_eq)
    return t, p, v, events, e_min, e_max


I_BUCK_MIN = 93e-3     # BQ25570 buck output current, min (typ 110 mA) at VSTOR 3.3 V, VOUT 1.8 V (SLUSBH2G)
V_ESP32_MIN = 3.0      # minimum supply of the ESP32 module
LEAK_PER_F = 10e-6     # bank leakage scaled with capacitance: 5 uW for the 0.5 F bank
MCUS = {"ESP32": (10e-6, 80e-3), "STM32L0": (0.9e-6, 5e-3), "MSP430FR": (0.5e-6, 1e-3),
        "nRF52832": (1.5e-6, 3.7e-3), "Apollo3": (1e-6, 0.5e-3)}     # (sleep, active current), Table 7


def design_checks():
    """Closed-form feasibility checks that complement the average-energy bound of Eq. 7."""
    window = 5.0 ** 2 - 3.5 ** 2
    out = {"bank_usable_J": 0.5 * 0.5 * window}
    out["c_required_F"] = {pl: 2 * e_event(pl) / ETA_BUCK / window for pl in ("lean", "sgp30", "mq135")}
    q_tx = (I_ACT + I_TX - I_BUCK_MIN) * TOA
    q_act = max(I_ACT + I_SENS - I_BUCK_MIN, 0.0) * 2.0
    esr = 0.5
    dv_cap = (V_CC - V_ESP32_MIN) - esr * (I_ACT + I_TX - I_BUCK_MIN)
    out["burst"] = {"rail_peak_A": I_ACT + I_TX, "deficit_charge_C": q_tx + q_act, "esr_ohm": esr,
                    "c_burst_min_F": (q_tx + q_act) / dv_cap}
    out["bank_current_max_A"] = V_CC * 110e-3 / (ETA_BUCK * 3.5)
    p_cell = 22e-6
    mcu = {}
    for k, (isl, iact) in MCUS.items():
        e = V_CC * (iact * 2.0 + I_SENS * 2.0) + E_TX
        fl = isl * V_CC
        ideal = p_cell - fl
        real = CASES["realistic"]["eta"] * p_cell - fl - CASES["realistic"]["pq"] - CASES["realistic"]["pleak"]
        mcu[k] = {"E_event_J": e, "ideal_h": e / ideal / 3600 if ideal > 0 else None,
                  "realistic_h": e / real / 3600 if real > 0 else None}
    out["mcu_22uW"] = mcu
    out["power_density_mW_m2"] = {"per_cell_22uW": 22e-6 / 0.01 * 1e3, "cell_15uW": 15e-6 / 0.01 * 1e3,
                                  "cell_30uW": 30e-6 / 0.01 * 1e3}
    rc = CASES["realistic"]
    p_off_rail = P_FLOOR + E_CHECK / (2.26 * 3600)
    p_off = p_off_rail / ETA_BUCK + rc["pq"] + rc["pleak"]
    out["bridge"] = {"p_off_bank_W": p_off, "check_share_W": E_CHECK / (2.26 * 3600) / ETA_BUCK,
                     "F_per_day": 2 * p_off * 86400 / window,
                     "F_per_day_without_checks": 2 * (P_FLOOR / ETA_BUCK + rc["pq"] + rc["pleak"]) * 86400 / window,
                     "leak_per_F_W": LEAK_PER_F,
                     "max_days_leak_scaled": window / 2 / (LEAK_PER_F * 86400)}
    fixed = p_off_rail / ETA_BUCK + rc["pq"]
    out["bridge"]["C_for_days_leak_scaled"] = {str(D): D * 86400 * fixed / (window / 2 - LEAK_PER_F * 86400 * D)
                                               for D in (1, 3, 5)}
    out["bridge_F_per_day"] = out["bridge"]["F_per_day"]
    out["burst_leak_per_uA_W"] = 1e-6 * V_CC
    out["lean_h_with_burst_leak_2uA"] = e_event("lean") / (p_net(150e-6, "realistic") - 2e-6 * V_CC) / 3600
    eta_in, eb = bank_terms("realistic")
    pn_bank = eta_in * 150e-6 - P_FLOOR / eb - rc["pq"] - rc["pleak"]
    out["lean_h_bank_referenced"] = e_event("lean") / eb / pn_bank / 3600
    out["branch_costs_J"] = {"sleep": E_CHECK, "measure": e_event("lean") - E_TX, "transmit": e_event("lean"),
                             "anomaly": e_event("lean")}
    return out


def trace_scenario(t_s, p_cell_W, n_cells=10, eta_stack=0.75, wake_h=2.26, case="realistic",
                   c_eq=0.5, v_max=5.0, v_min=3.5, restart_soc=0.05, pleak=None, policy="soc", reserve_J=0.0):
    """Algorithm 2 driven by a measured single-cell power trace (uniform step), with
    bank-referenced energy accounting (bank_terms). The array delivers n_cells * eta_stack *
    p_cell to the PMIC. Below v_min the buck drops out and the node is off (no sleep floor, the
    PMIC keeps charging); it restarts once the bank refills to restart_soc of the usable window
    and starts with that charge. Wakes follow a fixed grid of wake_h from the last restart and
    run at the first step at or after each grid time. A SLEEP wake pays the state-of-charge check
    on its own; for a measuring wake the check is part of the 2 s active window. pleak overrides
    the case leakage (e.g. LEAK_PER_F * c_eq for leakage that grows with capacitance).
    policy: "soc" = Algorithm 2 thresholds (0.25 / 0.55); "defer" = transmit when SoC >= 0.55,
    otherwise sleep without measuring; "reserve" = transmit when the usable energy covers one
    event plus reserve_J, otherwise sleep (independent of the bank size)."""
    cs = CASES[case]
    eta_in, eb = bank_terms(case)
    leak = cs["pleak"] if pleak is None else pleak
    e_min, e_max = 0.5 * c_eq * v_min ** 2, 0.5 * c_eq * v_max ** 2
    e_on = e_min + restart_soc * (e_max - e_min)
    e_lean = e_event("lean") / eb; e_meas = (e_event("lean") - E_TX) / eb; e_chk = E_CHECK / eb
    dt = float(t_s[1] - t_s[0])
    p_in = eta_in * n_cells * eta_stack * np.asarray(p_cell_W)
    E, on, nxt = e_on, True, wake_h * 3600
    n = len(t_s)
    v = np.empty(n); on_flag = np.zeros(n, bool)
    tx = np.zeros(n, int); counts = {"transmit": 0, "measure": 0, "sleep": 0}
    outages = 0
    for i in range(n):
        E += (p_in[i] - cs["pq"] - leak - (P_FLOOR / eb if on else 0.0)) * dt
        E = min(max(E, 0.0), e_max)
        if on and E < e_min:
            on = False; outages += 1
        elif not on and E >= e_on:
            on = True; nxt = t_s[i]
        if on and t_s[i] >= nxt:
            while nxt <= t_s[i]:
                nxt += wake_h * 3600
            soc = (E - e_min) / (e_max - e_min)
            if policy == "soc":
                act = "sleep" if soc < 0.25 else ("measure" if soc < 0.55 else "transmit")
            elif policy == "defer":
                act = "transmit" if soc >= 0.55 else "sleep"
            else:
                act = "transmit" if E - e_min >= e_lean + reserve_J else "sleep"
            if act == "sleep":
                E -= e_chk; counts["sleep"] += 1
            elif act == "measure":
                E -= e_meas; counts["measure"] += 1
            else:
                E -= e_lean; counts["transmit"] += 1; tx[i] = 1
            if E < e_min:
                on = False; outages += 1
        v[i] = np.sqrt(2 * E / c_eq); on_flag[i] = on
    return dict(v=v, on=on_flag, tx=tx, counts=counts, outages=outages, e_min=e_min, e_max=e_max)


if __name__ == "__main__":
    L = "=" * 74
    print(L); print("ENERGY-CHAIN MODEL  (physically realistic, three cases)"); print(L)

    print("\nPer-event energy (J):")
    for pl in ("lean", "lowgas", "mq135"):
        print(f"  {pl:8s}: {e_event(pl):8.3f} J")

    print(f"\nSustainable interval @150 uW (h)   [P_floor={P_FLOOR*1e6:.0f} uW]")
    print(f"  {'payload':10s} {'ideal':>8} {'realistic':>10} {'conservative':>13}")
    for pl in ("lean", "lowgas", "mq135"):
        vals = [interval_h(pl, 150e-6, c) for c in ("ideal", "realistic", "conservative")]
        print(f"  {pl:10s} " + " ".join(f"{v:>8.2f}" if np.isfinite(v) else f"{'inf':>8}" for v in
              [vals[0]]) + f" {vals[1]:>10.2f} {vals[2]:>13.2f}")

    print("\nP_net @150 uW (uW):")
    for c in CASES:
        print(f"  {c:12s}: {p_net(150e-6, c)*1e6:6.1f} uW")

    print("\n150 uW design point from stack:")
    print(f"  deterministic N (P_single=22uW, eta_stack=0.75): {cells_for_target()} cells")
    Nmc = mc_cells()
    print(f"  MC N: median={np.median(Nmc):.0f}, 5-95%=[{np.percentile(Nmc,5):.0f},"
          f"{np.percentile(Nmc,95):.0f}] cells")

    print("\nSupercap-bank ESR voltage-sag (120 mA conservative, full charge 5.0 V):")
    for esr in (1, 5, 12.5, 20):
        r = esr_constraint(esr, v_start=5.0)
        print(f"  ESR={esr:4.1f} ohm: sag={r['v_sag']:.2f} V, V_start_min={r['v_start_min']:.2f} V,"
              f" 5.0V-start {'OK' if r['ok'] else 'FAIL'}")

    print("\nMonte Carlo realistic lean interval (physical distributions):")
    dt, n_inf, n_tot = mc_interval(return_stats=True)
    print(f"  median={np.median(dt):.2f} h, 5-95%=[{np.percentile(dt,5):.2f},"
          f"{np.percentile(dt,95):.2f}] h, P(sub-2h)={100*np.mean(dt<2):.0f}%")
    print(f"  infeasible (P_net<=0): {n_inf}/{n_tot} ({100*n_inf/n_tot:.2f}%); "
          f"sub-hour observed: {int(np.sum(dt<1))}/{len(dt)}")

    print("\nSobol indices (loss-aware, N=65536):")
    sob = sobol_lossaware()
    sumS1 = sum(s1 for _, s1, _ in sob)
    for name, s1, st in sob:
        flag = "  <-- ST<S1 (sampling noise)" if st < s1 - 1e-9 else ""
        print(f"  {name:18s} S1={s1:.3f}  ST={st:.3f}{flag}")
    print(f"  sum(S1)={sumS1:.3f}")

    print("\nExternal validation:")
    mape, errs = ocv_mape()
    print(f"  OCV MAPE (model 0.86 vs 0.733/0.75/0.731) = {mape:.1f}%  per-study {[f'{e:.1f}%' for e in errs]}")
    cc = cadence_consistency()
    print(f"  Zheng ideal ESP32-lean @41uW = {cc['zheng_ideal_h']:.1f} h vs 23 h measured "
          f"(err {cc['zheng_ideal_err']:.1f}%)")
    print(f"  Zheng realistic P_net @41uW = {cc['zheng_realistic_pnet_uW']:.1f} uW -> "
          f"ESP32 {'feasible' if cc['zheng_realistic_feasible'] else 'INFEASIBLE'} "
          f"(explains nRF24 low-power node choice)")
    print(L)
