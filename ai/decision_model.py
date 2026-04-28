"""
Enerji Farkındalıklı İletim Karar Modeli
==========================================
RandomForest tabanlı sınıflandırıcı: mevcut enerji + sensör
verilerine bakarak 'sleep' / 'measure' / 'transmit' kararı verir.

Kural tabanlı eğitim verisi → model gerçek verilerle fine-tune edilebilir.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "decision_model.pkl")

ACTIONS = ["sleep", "measure", "transmit"]


class DecisionModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
        )
        self.encoder = LabelEncoder()
        self.trained = False

    def _label(self, energy: float, moisture: float, temp: float, ph: float) -> str:
        """
        Kural tabanlı etiket üreteci (eğitim verisi için).
        Gerçek öğrenme buraya bağlı kalır:
        - Enerji düşükse: uyu, kapasitörü doldur
        - Enerji ortadaysa: ölç, veriyi topla
        - Enerji yüksekse: gönder
        - Anomali varsa (düşük pH / yüksek nem vb.): zorla gönder
        """
        anomaly = (ph < 0.3 or ph > 0.85 or moisture < 0.05 or moisture > 0.95)
        if anomaly and energy > 0.35:
            return "transmit"
        if energy < 0.25:
            return "sleep"
        if energy < 0.55:
            return "measure"
        return "transmit"

    def train(self, n_samples: int = 2000):
        """Sentetik veriyle modeli eğit."""
        rng = np.random.default_rng(42)
        energy   = rng.random(n_samples)
        moisture = rng.random(n_samples)
        temp     = rng.random(n_samples)
        ph       = rng.random(n_samples)

        X = np.column_stack([energy, moisture, temp, ph])
        y_raw = [self._label(e, m, t, p) for e, m, t, p in zip(energy, moisture, temp, ph)]

        self.encoder.fit(ACTIONS)
        y = self.encoder.transform(y_raw)
        self.model.fit(X, y)
        self.trained = True

        acc = self.model.score(X, y)
        print(f"Model eğitildi — eğitim doğruluğu: {acc:.2%}")

    def predict(self, energy: float, moisture: float,
                temp: float, ph: float = 0.5) -> str:
        """Tek tahmin. Tüm girişler 0–1 normalize."""
        if not self.trained:
            self.train()
        X = np.array([[energy, moisture, temp, ph]])
        idx = self.model.predict(X)[0]
        return self.encoder.inverse_transform([idx])[0]

    def predict_proba(self, energy: float, moisture: float,
                      temp: float, ph: float = 0.5) -> dict:
        """Her eylem için olasılık döndür."""
        if not self.trained:
            self.train()
        X = np.array([[energy, moisture, temp, ph]])
        proba = self.model.predict_proba(X)[0]
        classes = self.encoder.inverse_transform(self.model.classes_)
        return dict(zip(classes, proba))

    def save(self, path: str = MODEL_PATH):
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"Model kaydedildi: {path}")

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "DecisionModel":
        with open(path, "rb") as f:
            return pickle.load(f)


if __name__ == "__main__":
    dm = DecisionModel()
    dm.train()

    test_cases = [
        (0.10, 0.5, 0.5, 0.5, "Düşük enerji"),
        (0.40, 0.5, 0.5, 0.5, "Orta enerji"),
        (0.80, 0.5, 0.5, 0.5, "Yüksek enerji"),
        (0.40, 0.02, 0.5, 0.5, "Anomali (kuraklık)"),
        (0.40, 0.5,  0.5, 0.1, "Anomali (düşük pH)"),
    ]
    print(f"\n{'Senaryo':<28} {'Karar':<12} {'Olasılıklar'}")
    print("-" * 70)
    for e, m, t, p, label in test_cases:
        decision = dm.predict(e, m, t, p)
        proba = dm.predict_proba(e, m, t, p)
        prob_str = "  ".join(f"{k}={v:.0%}" for k, v in proba.items())
        print(f"{label:<28} {decision:<12} {prob_str}")
