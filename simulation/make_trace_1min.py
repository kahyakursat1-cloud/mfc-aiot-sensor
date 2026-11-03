"""Write external/yen_smfc_trace_1min.csv: the single-cell trace of yen_trace.py at 1 min instead of 5 min
(input for the time-step sensitivity of the MATLAB trace runs)."""
import os, sys
import numpy as np
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import simulation.yen_trace as yt
yt.STEP = 60
r1 = yt.load_cells()
t_s, p = yt.load_trace("zero", r1)
pd.DataFrame({"t_s": t_s, "p_cell_W": p}).to_csv(os.path.join(ROOT, "external", "yen_smfc_trace_1min.csv"), index=False)
print(len(t_s), "steps;", "empty-bin share %.3f" % float(r1.isna().all(axis=1).mean()), "; mean cell power %.2f uW" % (p.mean() * 1e6))
