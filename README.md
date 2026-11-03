# Energy budget of battery-free Soil-MFC-powered AIoT sensor nodes

Code for the manuscript *Energy Budgeting and Sustainable Operating Limits of Battery-Free Soil Microbial
Fuel Cell-Powered AIoT Sensor Nodes: An Analytical and Simulation-Based Study* (Kürşat Kahya, Gülçin Mühürcü).

The model is analytical and simulation-based. No hardware prototype is part of this repository.

## Contents

| Folder | Content |
|---|---|
| `matlab/+ec` | the framework: event energy, net power, intervals, capacitor sizing, Monte Carlo, Sobol indices, cell count, trace-driven policies, rail transient, LoRa airtime, Isolation Forest workload |
| `matlab/tests` | 18 tests: 12 compare every headline number with the reference values in `matlab/python_reference.json`, 6 check the airtime formula, the rail transient, the MPPT operating point, the cold-start gate, and the pH settling time |
| `matlab/make_*.m` | figure scripts (see the table below) |
| `matlab/*_results.json` | stored outputs of `run_all.m` and `run_v27.m` |
| `simulation/`, `ai/` | independent reference implementation; `simulation/export_reference.py` writes `matlab/python_reference.json` |
| `python_figures/` | Figures 1 and 8 |

## Requirements

- MATLAB R2023b with the Statistics and Machine Learning Toolbox
- Python 3.10 or later with the packages in `requirements.txt` (reference values and Figures 1 and 8 only)

## Measured record

Section 4.4 uses the 161-day soil microbial fuel cell record of Yen et al.
(Proc. ACM Interact. Mob. Wearable Ubiquitous Technol. 7(4), 196, 2023, https://doi.org/10.1145/3631410).
The record is not redistributed here. To rebuild the 5 min trace:

```bash
git clone https://github.com/ka-moamoa/Practical_SMFC_Design_Guide external/yen_smfc
python simulation/yen_trace.py
```

This writes `external/yen_smfc_trace_5min.csv` (columns v0–v2 of `v3_Data.csv`, the three v3 cells across 2 kΩ).
`simulation/make_trace_1min.py` writes the 1 min trace used for the time-step check.

## Run

```matlab
cd matlab
run_tests   % 18 tests
run_all     % headline numbers, writes matlab_results.json
run_v27     % rail transient, policies, cold start, settling time; writes v27_results.json
```

```bash
python simulation/export_reference.py   # regenerates matlab/python_reference.json
```

## Figures

Create an output folder, for example `out = fullfile(pwd, 'figures'); mkdir(out)`, and pass it to each script.

| Figure | Script | File |
|---|---|---|
| 1 | `python python_figures/make_python_figures.py` | `fig1` |
| 2 | `make_fig_mfc_cell(out)` | `fig_mfc_cell` |
| 3 | `make_fig_schematic(out)` | `fig_schematic` |
| 4 | photograph by Cnd, Wikimedia Commons, CC0 1.0 (https://commons.wikimedia.org/w/index.php?curid=120157971), labelled | none |
| 5 | `make_figures(out)` | `fig4_lora` |
| 6 | `make_fig_comm_v2(out)` | `fig_comm_v2` |
| 7 | `make_figures(out)` | `fig10_relations` |
| 8 | `python python_figures/make_python_figures.py` | `fig_flowchart` |
| 9 | `make_fig_methods(out)` | `fig_methods_no_rf` |
| 10 | `make_fig_framework(out)` | `fig_pipeline` |
| 11 | `make_figures(out)` | `fig8_harvest_consume` |
| 12 | `make_figures(out)` | `fig2_energy_budget` |
| 13–20 | `make_fig_hoca(out)` | `fig13`–`fig20` |
| Graphical abstract | `make_fig_ga(out)` | |

Each script writes a 600 dpi PNG and a vector PDF. `make_figures` also writes figures that are not in the manuscript.

## Random seeds

Monte Carlo, Sobol, and the Isolation Forest use fixed seeds set in the functions of `matlab/+ec`. MATLAB and
Python use different random streams, so their stochastic results agree in distribution, not draw for draw.
