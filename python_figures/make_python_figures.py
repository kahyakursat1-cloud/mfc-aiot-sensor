"""Figures 1 and 8 of the manuscript (power-path flow and duty-cycling flowchart), PNG at 600 dpi and vector PDF.

Run from the repository root:  python python_figures/make_python_figures.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fig1_power_path
import make_figures

out = make_figures.OUT
fig1_power_path.render(os.path.join(out, "fig1.png"), 600)
fig1_power_path.render(os.path.join(out, "fig1.pdf"), 600)
make_figures.fig_flowchart()
png_save = make_figures.save
make_figures.save = lambda fig, name: png_save(fig, name.replace(".png", ".pdf"))
make_figures.fig_flowchart()
print("written to", out)
