"""
Anomali Tespit Modeli Eğitimi
==============================
Isolation Forest ile etiketlenmemiş çevre sensör verisi üzerinde
anomali tespiti. Gateway'de çalışır (edge'de değil).

Kullanım:
    python train.py                  # sentetik veriyle eğit
    python train.py --data gerçek.csv
"""

import argparse
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = ["soil_moisture", "temperature_c", "ph", "gas_ppm"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "anomaly_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")


# ── Sentetik veri üreteci ─────────────────────────────────────────────────────

def make_dataset(n_normal: int = 1200, n_anomaly: int = 80,
                 save_path: str = None) -> pd.DataFrame:
    rng = np.random.default_rng(0)

    normal = pd.DataFrame({
        "soil_moisture": rng.normal(45, 10, n_normal).clip(5, 95),
        "temperature_c": rng.normal(22,  5, n_normal).clip(-5, 50),
        "ph":            rng.normal(6.8, 0.5, n_normal).clip(4, 10),
        "gas_ppm":       rng.exponential(55, n_normal).clip(0, 600),
        "label": 0,
    })

    q = n_anomaly // 4
    anomalies = pd.concat([
        # Kuraklık
        pd.DataFrame({
            "soil_moisture": rng.normal(4,  1, q).clip(0, 10),
            "temperature_c": rng.normal(40, 3, q),
            "ph":            rng.normal(6.8, 0.5, q),
            "gas_ppm":       rng.exponential(55, q),
            "label": 1,
        }),
        # pH çöküşü
        pd.DataFrame({
            "soil_moisture": rng.normal(45, 10, q),
            "temperature_c": rng.normal(22,  5, q),
            "ph":            rng.normal(3.2, 0.3, q).clip(0, 5),
            "gas_ppm":       rng.exponential(55, q),
            "label": 1,
        }),
        # Gaz sızıntısı
        pd.DataFrame({
            "soil_moisture": rng.normal(45, 10, q),
            "temperature_c": rng.normal(22,  5, q),
            "ph":            rng.normal(6.8, 0.5, q),
            "gas_ppm":       rng.normal(900, 100, q).clip(600, 3000),
            "label": 1,
        }),
        # Su baskını
        pd.DataFrame({
            "soil_moisture": rng.normal(97,  2, n_anomaly - 3 * q).clip(92, 100),
            "temperature_c": rng.normal(22,  5, n_anomaly - 3 * q),
            "ph":            rng.normal(6.8, 0.5, n_anomaly - 3 * q),
            "gas_ppm":       rng.exponential(55, n_anomaly - 3 * q),
            "label": 1,
        }),
    ], ignore_index=True)

    df = pd.concat([normal, anomalies], ignore_index=True).sample(frac=1, random_state=1)
    df = df.reset_index(drop=True)

    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Veri kaydedildi: {save_path}  ({len(df)} satır)")
    return df


# ── Eğitim ───────────────────────────────────────────────────────────────────

def train(data_path: str = None) -> dict:
    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"Veri yüklendi: {data_path}  ({len(df)} satır)")
    else:
        csv_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
        df = make_dataset(save_path=csv_path)

    X = df[FEATURES].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Contamination = eğitim verisinde beklenen anomali oranı
    contamination = (df["label"] == 1).mean() if "label" in df.columns else 0.05
    model = IsolationForest(
        n_estimators=150,
        contamination=float(contamination),
        random_state=42,
        max_samples="auto",
    )
    model.fit(X_scaled)

    # Değerlendirme
    metrics = {}
    if "label" in df.columns:
        y_true = df["label"].values
        y_pred = (model.predict(X_scaled) == -1).astype(int)
        tp = int(((y_pred == 1) & (y_true == 1)).sum())
        fp = int(((y_pred == 1) & (y_true == 0)).sum())
        fn = int(((y_pred == 0) & (y_true == 1)).sum())
        prec = tp / max(1, tp + fp)
        rec  = tp / max(1, tp + fn)
        f1   = 2 * prec * rec / max(1e-9, prec + rec)
        metrics = {"precision": prec, "recall": rec, "f1": f1}
        print(f"\nModel Performansı:")
        print(f"  Precision : {prec:.3f}")
        print(f"  Recall    : {rec:.3f}")
        print(f"  F1        : {f1:.3f}")

    # Kaydet
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"\nModel → {MODEL_PATH}")
    print(f"Scaler → {SCALER_PATH}")
    return {"model": model, "scaler": scaler, **metrics}


# ── Tahmin (servis için) ──────────────────────────────────────────────────────

def predict(soil: float, temp: float, ph: float, gas: float) -> dict:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    X = scaler.transform([[soil, temp, ph, gas]])
    pred  = model.predict(X)[0]
    score = model.score_samples(X)[0]
    return {
        "anomaly": pred == -1,
        "score": float(score),
        "verdict": "ANOMALI 🚨" if pred == -1 else "Normal ✅",
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None, help="CSV veri dosyası")
    args = parser.parse_args()

    train(args.data)

    print("\n=== Örnek Tahminler ===")
    cases = [
        (45.0, 22.0, 6.8,  55.0, "Normal ortam"),
        ( 3.0, 40.0, 6.8,  55.0, "Kuraklık"),
        (45.0, 22.0, 3.2,  55.0, "pH çöküşü"),
        (45.0, 22.0, 6.8, 950.0, "Gaz sızıntısı"),
        (97.0, 20.0, 6.8,  40.0, "Su baskını"),
    ]
    print(f"  {'Senaryo':<18} {'Sonuç':<18} {'Skor':>8}")
    print(f"  {'-'*46}")
    for sm, tc, ph, gas, lbl in cases:
        r = predict(sm, tc, ph, gas)
        print(f"  {lbl:<18} {r['verdict']:<18} {r['score']:>8.3f}")
