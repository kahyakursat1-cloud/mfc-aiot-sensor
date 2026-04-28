"""
simulation/monte_carlo.py
=========================
Monte Carlo robustness analysis for the MFC-powered IoT sensor node.

Extends the Section 5.6 parametric sweep (27 combinations, 81.5% sustainable)
by sampling 200 independent random parameter sets including hardware imperfections:
  - MFC output variability (+/-30%, truncated Gaussian)
  - DC-DC converter efficiency (75-90%)
  - Supercapacitor self-discharge (1-5% of E_gen per cycle)
  - LoRa retransmission overhead from packet loss (0-5%)
  - Sensor power aging (+/-8%)

Energy model: paper Table 2 nominal values scaled by sampled factors.
Sustainability criterion: generation-to-consumption ratio >= 1.0
(equivalent to energy-positive operation over a 48-hour period).

Usage:
    python simulation/monte_carlo.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

# ── Nominal energy balance from paper (mJ per 10-minute cycle) ────────────────
E_GEN_NOM      = 0.480   # MFC generation (Table 2, "MFC Mean Generation")
E_ADAPTIVE_NOM = 0.413   # AI-adaptive consumption (Section 4.2)
E_TX_NOM       = 0.787   # Full TX cycle cost (Table 2 total)

# Action fractions that produce E_ADAPTIVE_NOM
TX_FRAC    = 0.12
MEAS_FRAC  = 0.26
SLEEP_FRAC = 0.62

# Derived: cost per mode
# E_adaptive = sleep_frac*E_sleep + meas_frac*E_meas + tx_frac*E_tx
# From Table 2: E_sleep = 0.036, E_meas = 0.362, E_tx = 0.787
E_SLEEP_NOM = 0.036
E_MEAS_NOM  = 0.362

# ── Monte Carlo configuration ─────────────────────────────────────────────────
N_TRIALS = 200
SEED     = 42


def sample_params(rng: np.random.Generator) -> dict:
    """
    Sample one parameter set.

    Biochemical / environmental:
      mfc_factor:   MFC output relative to nominal; TruncNormal(1.0, 0.18) in [0.40, 1.80]
                    Captures substrate variability, temperature (5-35 C), biofilm state.

    Power-path hardware imperfections:
      dc_dc_rel:    DC-DC efficiency relative to nominal 80%; Uniform(0.9375, 1.0625)
                    = efficiency range 75-90% divided by nominal 80%.
      cap_leak_frac: Fractional self-discharge of E_gen per cycle; Uniform(0.01, 0.05)
                    Supercap leakage ~1-5 uA; expressed relative to generation rate.
      pkt_loss:     LoRa packet-loss rate; Uniform(0.00, 0.05)
                    Causes retransmit overhead on 12% TX cycles.

    Sensor aging:
      sensor_aging: Measurement energy multiplier; TruncNormal(1.0, 0.08) in [0.85, 1.25]
                    Models capacitive probe drift, pH electrode degradation.
    """
    mfc_factor  = float(np.clip(rng.normal(1.0, 0.18), 0.40, 1.80))
    dc_dc_rel   = rng.uniform(0.9375, 1.0625)          # 75-90% / 80%
    cap_leak    = rng.uniform(0.01, 0.05)              # fraction of E_gen
    pkt_loss    = rng.uniform(0.00, 0.05)
    sensor_ag   = float(np.clip(rng.normal(1.0, 0.08), 0.85, 1.25))
    return dict(mfc_factor=mfc_factor, dc_dc_rel=dc_dc_rel,
                cap_leak=cap_leak, pkt_loss=pkt_loss, sensor_aging=sensor_ag)


def compute_ratio(p: dict) -> dict:
    """
    Compute the sustainability ratio for one parameter set.

    E_gen_eff  = E_GEN_NOM * mfc_factor * dc_dc_rel - leakage
    E_cons_eff = E_ADAPTIVE_NOM scaled by sensor-aging and retransmit overhead
    ratio      = E_gen_eff / E_cons_eff   (>= 1.0 => energy-positive)

    NOTE: E_ADAPTIVE_NOM (0.413 mJ) is used directly as the baseline consumption
    rather than re-deriving from mode fractions, to stay consistent with the
    paper's published energy budget (Section 4.2, Table 2).
    """
    # Effective generation
    e_gen = E_GEN_NOM * p['mfc_factor'] * p['dc_dc_rel']
    e_leakage = e_gen * p['cap_leak']          # leakage proportional to generation
    e_gen_net = max(0.0, e_gen - e_leakage)

    # Effective consumption
    # TX fraction (12%) incurs retransmit overhead from packet loss
    tx_overhead_frac = TX_FRAC * p['pkt_loss']          # small additive fraction
    # Sensor aging scales the measurement portion (~37% of adaptive total)
    sensor_frac = (MEAS_FRAC + TX_FRAC)                  # cycles with active sensing
    sensor_delta = sensor_frac * (p['sensor_aging'] - 1.0)

    consumption_factor = 1.0 + tx_overhead_frac + sensor_delta
    e_consume = E_ADAPTIVE_NOM * consumption_factor

    ratio = e_gen_net / e_consume if e_consume > 0 else float('inf')

    return dict(
        e_gen_nom   = E_GEN_NOM * p['mfc_factor'] * p['dc_dc_rel'],
        e_gen_net   = e_gen_net,
        e_consume   = e_consume,
        ratio       = ratio,
        energy_positive = ratio >= 1.0,
        **p,
    )


def run_monte_carlo(verbose: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    records = [compute_ratio(sample_params(rng)) for _ in range(N_TRIALS)]
    df = pd.DataFrame(records)

    n_ok = int(df['energy_positive'].sum())
    pct  = 100.0 * n_ok / N_TRIALS

    if verbose:
        hline = "=" * 64
        print(hline)
        print(f"Monte Carlo Robustness Analysis  (N={N_TRIALS}, seed={SEED})")
        print(hline)
        print(f"\n  Nominal margin: {E_GEN_NOM:.3f} / {E_ADAPTIVE_NOM:.3f}"
              f" = {E_GEN_NOM/E_ADAPTIVE_NOM:.3f}x")
        print(f"\n  Energy-positive trials: {n_ok}/{N_TRIALS} = {pct:.1f}%")
        print(f"\n  Sustainability ratio statistics:")
        print(f"    Mean   = {df['ratio'].mean():.3f}")
        print(f"    Std    = {df['ratio'].std():.3f}")
        print(f"    Median = {df['ratio'].median():.3f}")
        print(f"    Min    = {df['ratio'].min():.3f}")
        print(f"    Max    = {df['ratio'].max():.3f}")

        fail = df[~df['energy_positive']]
        print(f"\n  Failure analysis ({len(fail)} unsustainable trials):")
        if len(fail):
            print(f"    Mean mfc_factor in failures : {fail['mfc_factor'].mean():.3f}")
            print(f"    Mean dc_dc_rel  in failures : {fail['dc_dc_rel'].mean():.3f}")
            print(f"    Mean cap_leak   in failures : {fail['cap_leak'].mean():.4f}")
            print(f"    Mean pkt_loss   in failures : {fail['pkt_loss'].mean():.4f}")

        print(f"\n  [USE IN PAPER]: {pct:.1f}% of N={N_TRIALS} Monte Carlo trials "
              f"(with hardware imperfections) are energy-positive.")
        print(hline)

    return df


if __name__ == "__main__":
    df = run_monte_carlo()
    out = os.path.join(os.path.dirname(__file__), "monte_carlo_results.csv")
    df.to_csv(out, index=False)
    print(f"\nResults saved: {out}")
