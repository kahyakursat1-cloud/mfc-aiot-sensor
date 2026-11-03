"""
simulation/export_reference.py
Writes every headline number of the Python energy-chain model to
matlab/python_reference.json so the MATLAB implementation can be tested against it.

Run:  python simulation/export_reference.py
"""
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.energy_chain import (CASES, E_TX, I_ACT, I_SENS, I_TX, P_FLOOR, V_CC, e_event,
                                     interval_h, mc_cells, mc_interval, p_net, sobol_ci,
                                     dynamic_scenario)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "matlab", "python_reference.json")
CASE_NAMES = ["ideal", "realistic", "conservative"]
PAYLOADS = ["lean", "lowgas", "sgp30", "mq135"]


def dynamic_summary(wake_h):
    t, p, v, ev, e_min, e_max = dynamic_scenario(wake_h=wake_h)
    soc = (0.25 * v ** 2 - e_min) / (e_max - e_min)
    c = Counter(a for _, a, _, _ in ev)
    return dict(wake_h=wake_h,
                n_transmit=c["transmit"], n_measure=c["measure"], n_sleep=c["sleep"], n_anomaly=c["anomaly"],
                v_min=float(v.min()), v_max=float(v.max()), soc_min=float(soc.min()), soc_max=float(soc.max()),
                event_t_h=[float(tt / 3600) for tt, _, _, _ in ev],
                event_action=[a for _, a, _, _ in ev],
                event_v_before=[float(vb) for _, _, vb, _ in ev])


def main():
    ref = {}
    ref["e_event_J"] = {pl: e_event(pl) for pl in PAYLOADS}
    ref["e_tx_J"] = E_TX
    ref["p_floor_W"] = P_FLOOR
    ref["p_net_150uW_W"] = {c: p_net(150e-6, c) for c in CASE_NAMES}
    ref["interval_150uW_h"] = {pl: {c: interval_h(pl, 150e-6, c) for c in CASE_NAMES} for pl in PAYLOADS}
    demand = 144 * e_event("lean")
    ref["deficit_10min_x"] = {c: demand / (p_net(150e-6, c) * 86400) for c in CASE_NAMES}
    ref["daily_J"] = {"harvest": 150e-6 * 86400, **{f"net_{c}": p_net(150e-6, c) * 86400 for c in CASE_NAMES},
                      "demand_10min": demand}
    ref["zheng_41uW"] = {"ideal_h": interval_h("lean", 41e-6, "ideal"), "pnet_realistic_W": p_net(41e-6, "realistic")}

    dts = [12, 6, 3, 1, 0.5, 1 / 6]
    El = e_event("lean")
    ref["cells_vs_interval"] = {"dt_h": dts,
                                "N": [int(np.ceil((P_FLOOR + El / (d * 3600) + 1.6e-6 + 5e-6) / (0.80 * 0.75 * 22e-6)))
                                      for d in dts]}
    ref["cells_150uW_det"] = int(np.ceil(150e-6 / (22e-6 * 0.75)))
    Nmc = mc_cells()
    ref["cells_150uW_mc"] = {"median": float(np.median(Nmc)), "p5": float(np.percentile(Nmc, 5)),
                             "p95": float(np.percentile(Nmc, 95))}

    ref["esr_max_ohm"] = (5.0 - 3.5) / I_TX

    Pr = p_net(150e-6, "realistic"); Es = e_event("sgp30"); Em = e_event("mq135")
    def n_cells(E, dt_h):
        return int(np.ceil((P_FLOOR + E / (dt_h * 3600) + 1.6e-6 + 5e-6) / (0.80 * 0.75 * 22e-6)))
    ks = [1, 4, 8]
    rep = [((k - 1) * El + Es) / k / Pr / 3600 for k in ks]
    ref["gas_strategy"] = {"sgp30_every_k": ks, "report_h": rep, "gas_h": [r * k for r, k in zip(rep, ks)],
                           "mq135_gas_h": [72, 48, 24, 12, 6], "mq135_cells": [n_cells(Em, h) for h in (72, 48, 24, 12, 6)],
                           "sgp30_cells_2p3h": n_cells(Es, 2.3), "sgp30_continuous_W": 48.8e-3 * V_CC}

    t_act = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
    ref["wake_sweep_min"] = {"t_active_s": t_act,
                             **{c: [(V_CC * (I_ACT + I_SENS) * ti + E_TX) / p_net(150e-6, c) / 60 for ti in t_act]
                                for c in CASE_NAMES}}

    Pn = p_net(150e-6, "realistic"); Ef = e_event("mq135")
    fs = [0.0, 0.05, 0.10, 0.25, 1.0]
    tot = [Pn / ((1 - f) * El + f * Ef) * 86400 for f in fs]
    ref["pareto"] = {"f": fs, "total_per_day": tot, "gas_per_day": [f * r for f, r in zip(fs, tot)]}

    dt, n_inf, n_tot = mc_interval(return_stats=True)
    ref["mc_interval"] = {"n": n_tot, "n_infeasible": n_inf, "median_h": float(np.median(dt)),
                          "p5_h": float(np.percentile(dt, 5)), "p95_h": float(np.percentile(dt, 95)),
                          "frac_sub2h": float(np.mean(dt < 2)), "n_sub1h": int(np.sum(dt < 1)),
                          "min_h": float(dt.min())}

    sob = sobol_ci()
    ref["sobol"] = [dict(name=n, S1=s1, S1_lo=l1, S1_hi=h1, ST=st, ST_lo=l2, ST_hi=h2)
                    for n, s1, l1, h1, st, l2, h2 in sob]

    ref["dynamic"] = [dynamic_summary(1.9), dynamic_summary(2.26)]

    rng = np.random.default_rng(7); k = 400000
    cols = {"P_MFC": np.clip(rng.lognormal(np.log(150e-6), 0.20, k), 80e-6, 400e-6),
            "t_active": np.clip(rng.triangular(1.5, 2.0, 3.0, k), 1.5, 3.0),
            "eta_PMIC": (0.71 + 0.25 * rng.beta(5, 2, k)) * (0.86 + 0.07 * rng.beta(4, 3, k)),
            "P_leak": np.clip(rng.lognormal(np.log(5e-6), 0.5, k), 1e-6, 25e-6),
            "sensor_mult": np.clip(rng.normal(1.0, 0.15, k), 0.6, 1.4),
            "P_floor": np.clip(rng.normal(33e-6, 3e-6, k), 25e-6, 40e-6)}
    ref["input_moments"] = {n: {"mean": float(x.mean()), "std": float(x.std()), "p5": float(np.percentile(x, 5)),
                                "p95": float(np.percentile(x, 95))} for n, x in cols.items()}

    from simulation.energy_chain import design_checks
    ref["design_checks"] = design_checks()

    tr_path = os.path.join(os.path.dirname(OUT), "..", "external", "yen_smfc_trace_5min.csv")
    if os.path.exists(tr_path):
        from simulation.energy_chain import trace_scenario
        import pandas as pd
        tr = pd.read_csv(tr_path)
        ref["trace"] = []
        from simulation.energy_chain import LEAK_PER_F
        for n, c, lk in ((10, 0.5, None), (20, 0.5, None), (40, 5.0, None), (10, 5.0, LEAK_PER_F * 5.0)):
            r = trace_scenario(tr.t_s.values, tr.p_cell_W.values, n_cells=n, c_eq=c, pleak=lk)
            ref["trace"].append(dict(n_cells=n, c_eq=c, availability=float(r["on"].mean()), outages=int(r["outages"]),
                                     tx_total=int(r["tx"].sum()), n_transmit=r["counts"]["transmit"],
                                     n_measure=r["counts"]["measure"], n_sleep=r["counts"]["sleep"]))
        ref["policy_report_ratio"] = []
        ref["policy_availability"] = []
        for pol, res in (("soc", 0.0), ("defer", 0.0), ("reserve", 1.0), ("reserve", 0.0)):
            rr, aa = [], []
            for c, lk in ((0.5, None), (5.0, None), (5.0, LEAK_PER_F * 5.0)):
                r = trace_scenario(tr.t_s.values, tr.p_cell_W.values, n_cells=10, c_eq=c, pleak=lk, policy=pol, reserve_J=res)
                rr.append(float(r["tx"].sum() / (tr.t_s.values[-1] / (2.26 * 3600)))); aa.append(float(r["on"].mean()))
            ref["policy_report_ratio"].append(rr); ref["policy_availability"].append(aa)

    with open(OUT, "w", encoding="utf8") as f:
        json.dump(ref, f, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
