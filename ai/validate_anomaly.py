"""
ai/validate_anomaly.py
=======================
Runs proper Isolation Forest validation:
  - Scenario A: training data (seed=0, n_normal=1200, n_anomaly=200, 50/class)
  - Scenario B: independent validation data (seed=99, same distributions)
  - 5-fold stratified CV for aggregate metrics
  - Per-class breakdown on Scenario B holdout

Outputs numbers suitable for paper Section 4.4 and Figures 5 & 7.

Usage:
    python ai/validate_anomaly.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (precision_score, recall_score, f1_score,
                              accuracy_score, roc_auc_score,
                              confusion_matrix)

FEATURES = ["soil_moisture", "temperature_c", "ph", "gas_ppm"]
N_PER_CLASS = 50   # anomaly samples per class (upgrade from n=10)


def make_dataset(n_normal=1200, n_per_class=N_PER_CLASS, seed=0):
    """
    Generates labelled dataset with independent RNG seed.
    Normal samples: label=0
    Anomaly samples (4 classes): label=1
    """
    rng = np.random.default_rng(seed)
    n_anomaly = n_per_class * 4

    normal = pd.DataFrame({
        "soil_moisture": rng.normal(45, 10, n_normal).clip(5, 95),
        "temperature_c": rng.normal(22,  5, n_normal).clip(-5, 50),
        "ph":            rng.normal(6.8, 0.5, n_normal).clip(4, 10),
        "gas_ppm":       rng.exponential(55, n_normal).clip(0, 600),
        "label": 0,
        "class": "Normal",
    })

    drought = pd.DataFrame({
        "soil_moisture": rng.normal(4,  1.5, n_per_class).clip(0, 9),
        "temperature_c": rng.normal(40, 3,   n_per_class).clip(35, 55),
        "ph":            rng.normal(6.8, 0.5, n_per_class).clip(4, 10),
        "gas_ppm":       rng.exponential(55, n_per_class).clip(0, 600),
        "label": 1,
        "class": "Drought",
    })
    ph_crash = pd.DataFrame({
        "soil_moisture": rng.normal(45, 10, n_per_class).clip(5, 95),
        "temperature_c": rng.normal(22,  5, n_per_class).clip(-5, 50),
        "ph":            rng.normal(3.2, 0.3, n_per_class).clip(0, 4.5),
        "gas_ppm":       rng.exponential(55, n_per_class).clip(0, 600),
        "label": 1,
        "class": "pH Crash",
    })
    gas_spike = pd.DataFrame({
        "soil_moisture": rng.normal(45, 10, n_per_class).clip(5, 95),
        "temperature_c": rng.normal(22,  5, n_per_class).clip(-5, 50),
        "ph":            rng.normal(6.8, 0.5, n_per_class).clip(4, 10),
        "gas_ppm":       rng.normal(900, 100, n_per_class).clip(600, 3000),
        "label": 1,
        "class": "Gas Spike",
    })
    flood = pd.DataFrame({
        "soil_moisture": rng.normal(97, 2, n_per_class).clip(92, 100),
        "temperature_c": rng.normal(22, 5, n_per_class).clip(-5, 50),
        "ph":            rng.normal(6.8, 0.5, n_per_class).clip(4, 10),
        "gas_ppm":       rng.exponential(55, n_per_class).clip(0, 600),
        "label": 1,
        "class": "Flood",
    })

    df = pd.concat([normal, drought, ph_crash, gas_spike, flood],
                   ignore_index=True).sample(frac=1, random_state=seed)
    return df.reset_index(drop=True)


def run_validation():
    print("=" * 60)
    print("Isolation Forest Validation — n=50/class")
    print("=" * 60)

    # ── Train on Scenario A ────────────────────────────────────
    print("\nGenerating Scenario A (training, seed=0)...")
    df_a = make_dataset(n_normal=1200, n_per_class=N_PER_CLASS, seed=0)
    X_train = df_a[FEATURES].values
    y_train = df_a["label"].values

    contamination = y_train.mean()
    print(f"  Samples: {len(df_a)}  |  Contamination: {contamination:.3f}")

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)

    model = IsolationForest(
        n_estimators=150,
        contamination=float(contamination),
        random_state=42,
        max_samples="auto",
    )
    model.fit(X_train_s)

    # ── 5-fold CV on Scenario A ────────────────────────────────
    print("\nRunning 5-fold stratified CV on Scenario A...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_metrics = {"prec": [], "rec": [], "f1": [], "acc": [], "auc": []}

    for fold, (tr_idx, va_idx) in enumerate(skf.split(X_train_s, y_train)):
        X_tr, X_va = X_train_s[tr_idx], X_train_s[va_idx]
        y_tr, y_va = y_train[tr_idx],   y_train[va_idx]

        m = IsolationForest(n_estimators=150,
                            contamination=float(y_tr.mean()),
                            random_state=42, max_samples="auto")
        m.fit(X_tr)

        y_pred = (m.predict(X_va) == -1).astype(int)
        scores = -m.score_samples(X_va)

        cv_metrics["prec"].append(precision_score(y_va, y_pred, zero_division=0))
        cv_metrics["rec"].append(recall_score(y_va, y_pred, zero_division=0))
        cv_metrics["f1"].append(f1_score(y_va, y_pred, zero_division=0))
        cv_metrics["acc"].append(accuracy_score(y_va, y_pred))
        cv_metrics["auc"].append(roc_auc_score(y_va, scores))

    print("\n5-Fold CV Results (Scenario A):")
    cv_summary = {}
    for k, vals in cv_metrics.items():
        mu, sd = np.mean(vals), np.std(vals)
        cv_summary[k] = (mu, sd)
        print(f"  {k.upper():10s}: {mu:.3f} +/- {sd:.3f}")

    # ── Validate on Scenario B (independent holdout) ───────────
    print("\nGenerating Scenario B (validation, seed=99)...")
    df_b = make_dataset(n_normal=200, n_per_class=N_PER_CLASS, seed=99)
    X_val = scaler.transform(df_b[FEATURES].values)
    y_val = df_b["label"].values
    print(f"  Samples: {len(df_b)}  |  n_normal=200, n_per_class={N_PER_CLASS}")

    y_val_pred = (model.predict(X_val) == -1).astype(int)
    scores_val = -model.score_samples(X_val)

    print("\nScenario B Holdout Metrics:")
    print(f"  Precision : {precision_score(y_val, y_val_pred):.3f}")
    print(f"  Recall    : {recall_score(y_val, y_val_pred):.3f}")
    print(f"  F1        : {f1_score(y_val, y_val_pred):.3f}")
    print(f"  Accuracy  : {accuracy_score(y_val, y_val_pred):.3f}")
    print(f"  ROC-AUC   : {roc_auc_score(y_val, scores_val):.3f}")

    # ── Per-class breakdown on Scenario B ─────────────────────
    classes_order = ["Normal", "Drought", "pH Crash", "Gas Spike", "Flood"]
    print("\nPer-class breakdown (Scenario B, n=50 anomaly / 200 normal):")
    class_col = df_b["class"].values

    # Confusion matrix: rows = true, cols = predicted
    cm = confusion_matrix(y_val, y_val_pred)
    print(f"\nBinary confusion matrix:\n{cm}")

    # Per-class TP/FP/FN
    per_class = {}
    for cls in classes_order:
        mask = class_col == cls
        y_true_cls = y_val[mask]
        y_pred_cls = y_val_pred[mask]
        if cls == "Normal":
            tp = int(((y_pred_cls == 0) & (y_true_cls == 0)).sum())
            fp = int(((y_pred_cls == 1) & (y_true_cls == 0)).sum())
            per_class[cls] = {
                "n": int(mask.sum()),
                "correct": tp,
                "errors": fp,
                "recall": tp / max(1, tp + fp),
            }
        else:
            tp = int(((y_pred_cls == 1) & (y_true_cls == 1)).sum())
            fn = int(((y_pred_cls == 0) & (y_true_cls == 1)).sum())
            per_class[cls] = {
                "n": int(mask.sum()),
                "correct": tp,
                "errors": fn,
                "recall": tp / max(1, tp + fn),
            }

    print(f"\n{'Class':<12} {'n':>5} {'Correct':>8} {'Errors':>7} {'Recall':>7}")
    print("-" * 42)
    for cls, d in per_class.items():
        print(f"{cls:<12} {d['n']:>5} {d['correct']:>8} {d['errors']:>7} {d['recall']:>7.3f}")

    # Build 5x5 confusion matrix for figure
    cm5 = np.zeros((5, 5), dtype=int)
    for i, true_cls in enumerate(classes_order):
        for j, pred_cls in enumerate(classes_order):
            t_mask = class_col == true_cls
            # Map pred: Normal=0, others=1
            y_t = y_val[t_mask]
            y_p = y_val_pred[t_mask]
            # True class i → predicted as anomaly or normal
            if true_cls == "Normal":
                cm5[0, 0] = int(((y_p == 0)).sum())
                cm5[0, 1] = int(((y_p == 1)).sum())
                break
            else:
                if pred_cls != "Normal":
                    # For anomaly-to-anomaly mapping, all detected anomalies
                    # go to index 1 (we don't sub-classify)
                    pass

    # Simplified 5x5: actual counts per class (diagonal + misses)
    cm5_simple = np.zeros((5, 5), dtype=int)
    for i, cls in enumerate(classes_order):
        mask = class_col == cls
        y_t = y_val[mask]
        y_p = y_val_pred[mask]
        if cls == "Normal":
            detected_normal   = int((y_p == 0).sum())
            missed_as_anomaly = int((y_p == 1).sum())
            cm5_simple[0, 0] = detected_normal
            cm5_simple[0, 1] = missed_as_anomaly
        else:
            detected   = int((y_p == 1).sum())
            missed     = int((y_p == 0).sum())
            cm5_simple[i, i] = detected        # TP on diagonal
            cm5_simple[i, 0] = missed          # missed → predicted Normal

    print(f"\n5x5 Confusion Matrix (rows=True, cols=Pred):")
    print(f"{'':12}", end="")
    for c in classes_order:
        print(f"{c[:8]:>9}", end="")
    print()
    for i, c in enumerate(classes_order):
        print(f"{c:<12}", end="")
        for j in range(5):
            print(f"{cm5_simple[i,j]:>9}", end="")
        print()

    print("\n" + "=" * 60)
    print("PAPER UPDATE VALUES:")
    print("=" * 60)
    p_mu, p_sd = cv_summary["prec"]
    r_mu, r_sd = cv_summary["rec"]
    f_mu, f_sd = cv_summary["f1"]
    a_mu, a_sd = cv_summary["acc"]
    auc_mu, auc_sd = cv_summary["auc"]
    print(f"  5-fold CV (Scenario A, n_per_class=50):")
    print(f"    Precision : {p_mu:.3f} +/- {p_sd:.3f}")
    print(f"    Recall    : {r_mu:.3f} +/- {r_sd:.3f}")
    print(f"    F1-Score  : {f_mu:.3f} +/- {f_sd:.3f}")
    print(f"    Accuracy  : {a_mu:.3f} +/- {a_sd:.3f}")
    print(f"    ROC-AUC   : {auc_mu:.3f} +/- {auc_sd:.3f}")
    print(f"\n  Scenario B holdout (n=50/class):")
    print(f"    P={precision_score(y_val, y_val_pred):.3f}  "
          f"R={recall_score(y_val, y_val_pred):.3f}  "
          f"F1={f1_score(y_val, y_val_pred):.3f}  "
          f"AUC={roc_auc_score(y_val, scores_val):.3f}")
    print(f"\n  Per-class recall:")
    for cls, d in per_class.items():
        print(f"    {cls:<12}: recall={d['recall']:.3f}  ({d['correct']}/{d['n']})")
    print(f"\n  5x5 CM (use in figure 7):")
    print(f"  {cm5_simple.tolist()}")

    return {
        "cv": cv_summary,
        "cm5": cm5_simple,
        "per_class": per_class,
        "holdout_f1": f1_score(y_val, y_val_pred),
        "holdout_auc": roc_auc_score(y_val, scores_val),
    }


if __name__ == "__main__":
    run_validation()
