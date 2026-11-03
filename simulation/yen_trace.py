"""
simulation/yen_trace.py
Trace-driven test of the framework on the measured soil-MFC power of Yen et al. (2023),
"Soil-Powered Computing", data from github.com/ka-moamoa/Practical_SMFC_Design_Guide
(file Data/design_iterations/v3_Data.csv; not redistributed, clone it into external/yen_smfc).

The three v3 cells (columns v0, v1, v2, mV across a fixed 2 kOhm load) give per-cell power
P = V^2 / 2000 (negative voltages clipped to zero); the single-cell trace is the mean over the
cells that report at each 1-min sample, resampled to 5-min means. 5-min bins in which no cell
reports (recording gaps) are set to zero power in the baseline; the sensitivity runs
interpolate them instead. Writes simulation/yen_trace_results.json and
external/yen_smfc_trace_5min.csv (input for the MATLAB port).

Run:  python simulation/yen_trace.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from simulation.energy_chain import LEAK_PER_F, interval_h, trace_scenario

SRC = os.path.join(ROOT, "external", "yen_smfc", "Data", "design_iterations", "v3_Data.csv")
STEP = 300
WAKE_H = 2.26


def load_cells():
    df = pd.read_csv(SRC, low_memory=False, usecols=["unix_time", "v0", "v1", "v2"])
    t = pd.to_datetime(df.unix_time.astype(float).values, unit="s")
    cells = pd.DataFrame({c: (pd.to_numeric(df[c], errors="coerce").clip(lower=0) / 1000.0) ** 2 / 2000.0
                          for c in ("v0", "v1", "v2")}).set_index(t)
    return cells.resample(f"{STEP}s").mean()


def load_trace(fill="zero", r5=None):
    r5 = load_cells() if r5 is None else r5
    s = r5.mean(axis=1, skipna=True)
    s = s.fillna(0.0) if fill == "zero" else s.interpolate(limit_direction="both")
    return (s.index - s.index[0]).total_seconds().values, s.values


def summarise(res, t_s):
    days = t_s[-1] / 86400
    tx_day = pd.Series(res["tx"], index=pd.to_timedelta(t_s, unit="s")).resample("1D").sum()
    off = ~res["on"]
    runs, cur = [], 0
    for o in off:
        cur = cur + 1 if o else 0
        runs.append(cur)
    scheduled = t_s[-1] / (WAKE_H * 3600)
    return dict(availability=float(res["on"].mean()), outages=int(res["outages"]),
                longest_outage_days=float(max(runs) * STEP / 86400),
                tx_total=int(res["tx"].sum()), tx_per_day_mean=float(res["tx"].sum() / days),
                report_ratio=float(res["tx"].sum() / scheduled),
                days_without_tx=int((tx_day == 0).sum()), days=int(round(days)), counts=res["counts"])


def main():
    r5 = load_cells()
    t_s, p = load_trace("zero", r5)
    pd.DataFrame({"t_s": t_s, "p_cell_W": p}).to_csv(os.path.join(ROOT, "external", "yen_smfc_trace_5min.csv"), index=False)
    daily = pd.Series(p, index=pd.to_timedelta(t_s, unit="s")).resample("1D").mean() * 1e6
    cell_daily = r5.resample("1D").mean() * 1e6
    gap = r5.isna().all(axis=1)
    gap_runs = gap.astype(int).groupby((~gap).cumsum()).sum()
    low = daily < 5
    low_runs = low.astype(int).groupby((~low).cumsum()).sum()
    corr = cell_daily.corr()
    out = {"source": "Yen et al. v3 cells (v0-v2), 2 kOhm load, 5-min mean, gaps = 0",
           "file": "Data/design_iterations/v3_Data.csv",
           "start": str(r5.index[0]), "end": str(r5.index[-1]),
           "days": int(round(t_s[-1] / 86400)), "step_s": STEP, "wake_h": WAKE_H,
           "gap_fraction": float(gap.mean()), "gap_days": float(gap.sum() * STEP / 86400),
           "longest_gap_days": float(gap_runs.max() * STEP / 86400),
           "cell_mean_uW": float(p.mean() * 1e6), "cell_median_uW": float(np.median(p) * 1e6),
           "daily_cell_uW": {"median": float(daily.median()), "p5": float(daily.quantile(.05)), "p95": float(daily.quantile(.95))},
           "days_below_5uW": int(low.sum()), "longest_run_below_5uW_days": int(low_runs.max()),
           "days_below_15uW": int((daily < 15).sum()),
           "days_all_cells_below_5uW": int((cell_daily < 5).all(axis=1).sum()),
           "cell_daily_corr": {"min": float(corr.values[np.triu_indices(3, 1)].min()),
                               "max": float(corr.values[np.triu_indices(3, 1)].max())},
           "array10_daily_cv": float((daily * 7.5).std() / (daily * 7.5).mean()),
           "runs": [], "sensitivity": []}
    for n in (10, 20, 40):
        for c in (0.5, 5.0):
            r = summarise(trace_scenario(t_s, p, n_cells=n, wake_h=WAKE_H, c_eq=c), t_s)
            r.update(n_cells=n, c_eq=c,
                     mean_array_uW=float(n * 0.75 * p.mean() * 1e6),
                     eq7_interval_at_mean_h=float(interval_h("lean", n * 0.75 * p.mean(), "realistic")))
            out["runs"].append(r)
    t_i, p_i = load_trace("interp", r5)
    cases = [("baseline", t_s, p, 0.5, None), ("gaps interpolated", t_i, p_i, 0.5, None),
             ("5 F, leakage fixed", t_s, p, 5.0, None), ("5 F, gaps interpolated", t_i, p_i, 5.0, None)]
    cases += [(f"{c:g} F, leakage scaled", t_s, p, c, LEAK_PER_F * c) for c in (1.0, 2.0, 5.0)]
    for label, ts, pp, c, lk in cases:
        r = summarise(trace_scenario(ts, pp, n_cells=10, wake_h=WAKE_H, c_eq=c, pleak=lk), ts)
        r.update(label=label, c_eq=c, pleak_uW=(5.0 if lk is None else lk * 1e6))
        out["sensitivity"].append(r)
    banks = [("0.5 F, 5 uW", 0.5, None), ("5 F, 5 uW", 5.0, None), ("5 F, 50 uW", 5.0, LEAK_PER_F * 5.0)]
    pols = [("Algorithm 2 thresholds", "soc", 0.0), ("Defer measurement", "defer", 0.0),
            ("Energy reserve 1 J", "reserve", 1.0), ("Greedy (one event stored)", "reserve", 0.0)]
    out["policies"] = []
    for plab, pol, res in pols:
        row = {"policy": plab}
        for blab, c, lk in banks:
            r = summarise(trace_scenario(t_s, p, n_cells=10, wake_h=WAKE_H, c_eq=c, pleak=lk, policy=pol, reserve_J=res), t_s)
            row[blab] = {"availability": r["availability"], "report_ratio": r["report_ratio"], "outages": r["outages"]}
        out["policies"].append(row)
    T = t_s[-1]; sched = T / (WAKE_H * 3600); P10 = 10 * 0.75 * p
    from simulation.energy_chain import e_event, p_net
    E = e_event("lean")
    out["ablation"] = {
        "A_mean_harvest_event_energy": min(1.0, P10.mean() * T / E / sched),
        "B_plus_floor_and_losses": min(1.0, max(p_net(P10.mean(), "realistic"), 0.0) * T / E / sched),
        "C_plus_finite_storage_greedy": out["policies"][3]["0.5 F, 5 uW"]["report_ratio"],
        "D_plus_algorithm2": out["policies"][0]["0.5 F, 5 uW"]["report_ratio"]}
    json.dump(out, open(os.path.join(ROOT, "simulation", "yen_trace_results.json"), "w"), indent=1)
    print(json.dumps({"policies": out["policies"], "ablation": out["ablation"]}, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("runs", "sensitivity")}, indent=1))
    for r in out["runs"] + out["sensitivity"]:
        print(f"{r.get('label', '')!s:24s} N={r.get('n_cells', 10):2d} C={r['c_eq']:.1f} F: avail {r['availability']:.3f}, "
              f"reports {r['report_ratio']:.3f}, outages {r['outages']}, longest {r['longest_outage_days']:.1f} d, "
              f"days w/o tx {r['days_without_tx']}/{r['days']}, counts {r['counts']}")


if __name__ == "__main__":
    main()
