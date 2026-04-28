"""
ChartPanel — pyqtgraph ile gerçek zamanlı sensör grafikleri.
Her node farklı renkte, canlı kaydırmalı pencere.
"""

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                                 QLabel, QPushButton, QButtonGroup)
from PySide6.QtCore import Qt

from dashboard.styles import C, PG_BACKGROUND, PG_FOREGROUND, NODE_COLORS, CHART_METRICS


class ChartPanel(QFrame):
    """
    Seçili metriği tüm node'lar için gerçek zamanlı gösterir.
    Üstteki butonlarla metrik değiştirilebilir.
    """

    WINDOW = 150   # gösterilen son N nokta

    def __init__(self, data_source, n_nodes: int = 3, parent=None):
        super().__init__(parent)
        self.ds       = data_source
        self.n_nodes  = n_nodes
        self.setObjectName("chartPanel")

        # pyqtgraph global ayarları
        pg.setConfigOptions(
            background=PG_BACKGROUND,
            foreground=PG_FOREGROUND,
            antialias=True,
        )

        self._metric = "soil_moisture"   # aktif metrik
        self._curves: dict[int, pg.PlotDataItem] = {}
        self._threshold_lines: list = []

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # ── Başlık + metrik seçici ─────────────────────────────────────
        top = QHBoxLayout()

        self._title_lbl = QLabel("CANLI VERİ")
        self._title_lbl.setObjectName("chartTitle")
        top.addWidget(self._title_lbl)
        top.addStretch()

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for key, (name, unit, *_) in CHART_METRICS.items():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(22)
            if key == self._metric:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, k=key: self._set_metric(k))
            self._btn_group.addButton(btn)
            top.addWidget(btn)

        layout.addLayout(top)

        # ── pyqtgraph PlotWidget ───────────────────────────────────────
        self._plot = pg.PlotWidget()
        self._plot.setMinimumHeight(180)
        self._plot.showGrid(x=False, y=True, alpha=0.15)
        self._plot.getAxis("left").setTextPen(pg.mkPen(color=C["TEXT_SEC"]))
        self._plot.getAxis("bottom").setTextPen(pg.mkPen(color=C["TEXT_SEC"]))
        self._plot.getAxis("left").setPen(pg.mkPen(color=C["BORDER"]))
        self._plot.getAxis("bottom").setPen(pg.mkPen(color=C["BORDER"]))
        self._plot.setMouseEnabled(x=False, y=True)

        # Legend
        self._legend = self._plot.addLegend(
            offset=(10, 10),
            labelTextColor=C["TEXT_SEC"],
        )

        # Node eğrileri
        for i in range(self.n_nodes):
            nid   = i + 1
            color = NODE_COLORS[i % len(NODE_COLORS)]
            curve = self._plot.plot(
                [],
                pen=pg.mkPen(color=color, width=2),
                name=f"Node {nid}",
            )
            self._curves[nid] = curve

        layout.addWidget(self._plot)

        # ── Node renk efsanesi (manuel) ────────────────────────────────
        legend_row = QHBoxLayout()
        legend_row.addStretch()
        for i in range(self.n_nodes):
            dot = QLabel(f"● Node {i+1}")
            dot.setStyleSheet(
                f"color:{NODE_COLORS[i % len(NODE_COLORS)]}; font-size:10px;")
            legend_row.addWidget(dot)
            if i < self.n_nodes - 1:
                legend_row.addSpacing(12)
        legend_row.addStretch()
        layout.addLayout(legend_row)

        self._apply_metric()

    # ── Metrik değiştir ───────────────────────────────────────────────────────

    def _set_metric(self, key: str):
        self._metric = key
        self._apply_metric()

    def _apply_metric(self):
        name, unit, ymin, ymax, color = CHART_METRICS[self._metric]
        self._title_lbl.setText(f"CANLI VERİ  ·  {name.upper()}")
        self._plot.setYRange(ymin, ymax, padding=0.05)
        self._plot.getAxis("left").setLabel(f"{name} ({unit})" if unit else name)

        # Eşik çizgileri
        for line in self._threshold_lines:
            self._plot.removeItem(line)
        self._threshold_lines.clear()

        thresholds = {
            "soil_moisture": [(10, C["WARNING"], "--"), (92, C["WARNING"], "--")],
            "ph":            [(4.5, C["DANGER"], "--"), (8.5, C["DANGER"], "--")],
            "gas_ppm":       [(400, C["DANGER"], "--")],
            "temperature_c": [(40, C["WARNING"], "--")],
        }
        for val, col, style in thresholds.get(self._metric, []):
            line = pg.InfiniteLine(
                pos=val, angle=0,
                pen=pg.mkPen(color=col, width=1, style=Qt.DashLine),
            )
            self._plot.addItem(line)
            self._threshold_lines.append(line)

    # ── Veri güncelleme ───────────────────────────────────────────────────────

    def refresh(self):
        """data_source'dan geçmiş veriyi çek, grafikleri güncelle."""
        for nid, curve in self._curves.items():
            data = self.ds.history(nid, self._metric, n=self.WINDOW)
            if len(data) == 0:
                continue
            x = np.arange(len(data))
            curve.setData(x, data)
