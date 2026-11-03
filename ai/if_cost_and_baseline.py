"""
ai/if_cost_and_baseline.py
Size and inference cost of the 150-tree Isolation Forest, and a simple threshold baseline on the
same synthetic data (Scenario A training set, Scenario B independent hold-out).
Writes ai/if_cost_and_baseline.json.

Run:  python ai/if_cost_and_baseline.py
"""
import json
import os
import sys

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ai.validate_anomaly import FEATURES, make_dataset
from simulation.energy_chain import I_ACT, V_CC

CYCLES_PER_NODE = 20          # assumption: compare, branch and load per visited node on a 240 MHz ESP32
F_CPU = 240e6


def main():
    a = make_dataset(seed=0); b = make_dataset(seed=99)
    sc = StandardScaler().fit(a[FEATURES].values)
    Xa, ya = sc.transform(a[FEATURES].values), a["label"].values
    Xb, yb = sc.transform(b[FEATURES].values), b["label"].values
    m = IsolationForest(n_estimators=150, contamination=float(ya.mean()), random_state=42, max_samples="auto").fit(Xa)

    nodes = sum(t.tree_.node_count for t in m.estimators_)
    leaves = sum(int((t.tree_.children_left == -1).sum()) for t in m.estimators_)
    internal = nodes - leaves
    depth_max = max(t.tree_.max_depth for t in m.estimators_)
    visits = np.mean([sum(t.decision_path(Xb[:, f]).sum(axis=1).A1[i] for t, f in zip(m.estimators_, m.estimators_features_))
                      for i in range(len(Xb))])
    mem_bytes = internal * (1 + 4 + 2 + 2) + leaves * 4
    t_inf = visits * CYCLES_PER_NODE / F_CPU
    e_inf = V_CC * I_ACT * t_inf

    pred_if = (m.predict(Xb) == -1).astype(int)
    z = np.abs(Xb)
    pred_thr = (z > 3).any(axis=1).astype(int)
    def scores(y, p): return dict(precision=float(precision_score(y, p)), recall=float(recall_score(y, p)), f1=float(f1_score(y, p)))

    out = dict(n_trees=150, n_features=len(FEATURES), total_nodes=int(nodes), internal_nodes=int(internal), leaves=int(leaves),
               max_depth=int(depth_max), mean_node_visits_per_inference=float(visits), model_bytes_estimate=int(mem_bytes),
               cycles_per_node_assumed=CYCLES_PER_NODE, inference_time_s=float(t_inf), inference_energy_J=float(e_inf),
               assumed_cost_in_paper_J=3e-3,
               holdout_isolation_forest=scores(yb, pred_if), holdout_threshold_z3=scores(yb, pred_thr))
    json.dump(out, open(os.path.join(ROOT, "ai", "if_cost_and_baseline.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
