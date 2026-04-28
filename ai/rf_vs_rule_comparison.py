"""
ai/rf_vs_rule_comparison.py
============================
Quantitative comparison of Random Forest decision model vs. deterministic
rule-based logic under simulated SoC measurement noise.

Demonstrates the RF advantage: reduced oscillation near threshold boundaries
and fewer failed transmissions due to SoC overestimation under noise.

Usage:
    python ai/rf_vs_rule_comparison.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from ai.decision_model import DecisionModel

# Paper Table 2 energy values (mJ per cycle)
ENERGY_mJ = {
    "sleep":    0.011,
    "measure":  0.073,   # ESP32 active + sensors (no TX)
    "transmit": 0.787,
}

E_CAP_MAX_J = 5.445   # 0.5 * 1F * 3.3^2  (paper eq.)
SOC_SLEEP_THRESH    = 0.25
SOC_MEASURE_THRESH  = 0.55


def rule_decision(soc: float) -> str:
    if soc < SOC_SLEEP_THRESH:
        return "sleep"
    if soc < SOC_MEASURE_THRESH:
        return "measure"
    return "transmit"


def simulate(strategy, n_cycles: int = 2000,
             noise_sigma: float = 0.05, seed: int = 42) -> dict:
    """
    strategy: "rule" or a trained DecisionModel instance.
    Returns a dict of performance metrics.
    """
    rng = np.random.default_rng(seed)

    # MFC generation: mean 0.48 mJ, std 0.10 mJ (paper Section 4.2)
    mfc_gen_mJ = rng.normal(0.48, 0.10, n_cycles).clip(0.05, 1.5)

    E_J = 0.60 * E_CAP_MAX_J   # start at 60% SoC
    soc = E_J / E_CAP_MAX_J

    total_energy_mJ = 0.0
    actions = []
    last_action = None
    oscillations = 0
    depletion_events = 0   # SoC < 0.10
    tx_failed = 0          # wanted transmit but had no energy

    # Sensor feature noise for RF (normalized, 0-1)
    moisture_seq = rng.normal(0.45, 0.12, n_cycles).clip(0, 1)
    temp_seq     = rng.normal(0.40, 0.09, n_cycles).clip(0, 1)
    ph_seq       = rng.normal(0.49, 0.04, n_cycles).clip(0, 1)

    for i in range(n_cycles):
        # Charge from MFC
        E_J = min(E_J + mfc_gen_mJ[i] * 1e-3, E_CAP_MAX_J)
        soc = E_J / E_CAP_MAX_J

        # Add Gaussian noise to SoC reading
        soc_noisy = float(np.clip(soc + rng.normal(0, noise_sigma), 0.0, 1.0))

        # Decision
        if strategy == "rule":
            decision = rule_decision(soc_noisy)
        else:
            decision = strategy.predict(soc_noisy,
                                        moisture_seq[i],
                                        temp_seq[i],
                                        ph_seq[i])

        # Oscillation: consecutive decision change
        if last_action is not None and decision != last_action:
            oscillations += 1
        last_action = decision

        # Consume energy; handle insufficient energy
        cost_J = ENERGY_mJ[decision] * 1e-3
        if E_J >= cost_J:
            E_J -= cost_J
            total_energy_mJ += ENERGY_mJ[decision]
            actions.append(decision)
        else:
            # Fall back to sleep
            sleep_J = ENERGY_mJ["sleep"] * 1e-3
            E_J -= sleep_J
            total_energy_mJ += ENERGY_mJ["sleep"]
            actions.append("sleep")
            if decision == "transmit":
                tx_failed += 1

        soc = E_J / E_CAP_MAX_J
        if soc < 0.10:
            depletion_events += 1

    n = len(actions)
    return {
        "avg_energy_mj":    total_energy_mJ / n,
        "sleep_frac":       actions.count("sleep")    / n,
        "measure_frac":     actions.count("measure")  / n,
        "tx_frac":          actions.count("transmit") / n,
        "oscillation_rate": oscillations / n,
        "depletion_events": depletion_events,
        "tx_failed":        tx_failed,
    }


def main():
    print("Training RF model (seed=42, n_samples=3000)...")
    rf = DecisionModel()
    rf.train(n_samples=3000)
    print()

    noise_levels = [0.00, 0.02, 0.05, 0.10]
    header = (f"{'Noise s':>8}  {'Strategy':>10}  {'Avg E(mJ)':>10}  "
              f"{'TX%':>6}  {'Meas%':>7}  {'Sleep%':>7}  "
              f"{'Osc.Rate':>9}  {'TXfail':>7}  {'Deplet':>7}")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    results = {}
    for sigma in noise_levels:
        for name, strat in [("rule", "rule"), ("RF", rf)]:
            r = simulate(strat, n_cycles=2000, noise_sigma=sigma, seed=42)
            results[(sigma, name)] = r
            print(
                f"{sigma:>8.2f}  {name:>10}  {r['avg_energy_mj']:>10.3f}  "
                f"{r['tx_frac']:>6.1%}  {r['measure_frac']:>7.1%}  "
                f"{r['sleep_frac']:>7.1%}  {r['oscillation_rate']:>9.3f}  "
                f"{r['tx_failed']:>7d}  {r['depletion_events']:>7d}"
            )
        print()

    # Summary for paper table
    print("=" * 72)
    print("PAPER TABLE SUMMARY (noise σ = 0.05, n_cycles = 2000)")
    print("=" * 72)
    for sigma in [0.05, 0.10]:
        r_rule = results[(sigma, "rule")]
        r_rf   = results[(sigma, "RF")]
        e_save  = (r_rule['avg_energy_mj'] - r_rf['avg_energy_mj']) / r_rule['avg_energy_mj'] * 100
        osc_red = (r_rule['oscillation_rate'] - r_rf['oscillation_rate']) / max(r_rule['oscillation_rate'], 1e-9) * 100
        print(f"\nNoise s = {sigma:.2f}:")
        print(f"  Rule avg energy : {r_rule['avg_energy_mj']:.3f} mJ/cycle")
        print(f"  RF   avg energy : {r_rf['avg_energy_mj']:.3f} mJ/cycle")
        print(f"  Energy saving   : {e_save:+.1f}%")
        print(f"  Rule osc. rate  : {r_rule['oscillation_rate']:.3f}")
        print(f"  RF   osc. rate  : {r_rf['oscillation_rate']:.3f}")
        print(f"  Osc. reduction  : {osc_red:+.1f}%")
        print(f"  Rule TX failed  : {r_rule['tx_failed']}")
        print(f"  RF   TX failed  : {r_rf['tx_failed']}")
        print(f"  Rule depletions : {r_rule['depletion_events']}")
        print(f"  RF   depletions : {r_rf['depletion_events']}")


if __name__ == "__main__":
    main()
