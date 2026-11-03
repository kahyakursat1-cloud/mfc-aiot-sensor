"""
simulation/sobol_seed_stability.py
Why the Sobol indices are computed on the reporting rate r* = P_net/E_event and not on
the interval Dt = 1/r*: repeats the Saltelli estimate over eight seeds for both outputs
and writes the spread to simulation/sobol_seed_stability.json.

Run:  python simulation/sobol_seed_stability.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.energy_chain import E_TX, I_ACT, I_SENS, V_CC

NAMES = ["Harvested power", "Active duration", "PMIC efficiency", "Supercap leakage", "Sensor current", "Sleep floor"]


def indices(seed, output, n=32768):
    rng = np.random.default_rng(seed)

    def smp(k):
        return np.column_stack([
            np.clip(rng.lognormal(np.log(150e-6), 0.20, k), 80e-6, 400e-6),
            np.clip(rng.triangular(1.5, 2.0, 3.0, k), 1.5, 3.0),
            (0.71 + 0.25 * rng.beta(5, 2, k)) * (0.86 + 0.07 * rng.beta(4, 3, k)),
            np.clip(rng.lognormal(np.log(5e-6), 0.5, k), 1e-6, 25e-6),
            np.clip(rng.normal(1.0, 0.15, k), 0.6, 1.4),
            np.clip(rng.normal(33e-6, 3e-6, k), 25e-6, 40e-6)])

    def model(X):
        p, t, eta, leak, sm, fl = X.T
        e = V_CC * (I_ACT * t + I_SENS * t * sm) + E_TX
        pn = eta * p - fl - 1.6e-6 - leak
        if output == "rate":
            return pn / e * 86400.0
        return np.where(pn > 0, e / pn / 3600.0, 50.0)

    A, B = smp(n), smp(n)
    yA, yB = model(A), model(B)
    v = np.var(np.concatenate([yA, yB]))
    out = []
    for i in range(6):
        AB = A.copy(); AB[:, i] = B[:, i]
        yAB = model(AB)
        out.append((max(np.mean(yB * (yAB - yA)) / v, 0.0), 0.5 * np.mean((yA - yAB) ** 2) / v))
    return out


def main():
    seeds = list(range(1, 9))
    res = {}
    for output in ("interval", "rate"):
        runs = [indices(s, output) for s in seeds]
        res[output] = {name: {"S1_min": min(r[i][0] for r in runs), "S1_max": max(r[i][0] for r in runs),
                              "ST_min": min(r[i][1] for r in runs), "ST_max": max(r[i][1] for r in runs)}
                       for i, name in enumerate(NAMES)}
        res[output]["sum_S1_range"] = [min(sum(x[0] for x in r) for r in runs), max(sum(x[0] for x in r) for r in runs)]
    res["seeds"] = seeds
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sobol_seed_stability.json")
    json.dump(res, open(out, "w", encoding="utf8"), indent=1)
    for output in ("interval", "rate"):
        h = res[output]["Harvested power"]
        print(f"{output:8s} harvested power  S1 {h['S1_min']:.3f}-{h['S1_max']:.3f}  ST {h['ST_min']:.3f}-{h['ST_max']:.3f}"
              f"  sum S1 {res[output]['sum_S1_range'][0]:.3f}-{res[output]['sum_S1_range'][1]:.3f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
