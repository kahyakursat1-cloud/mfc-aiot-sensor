"""
NodeCard — Tek sensör node'u kartı.
Sol: EnergyGauge | Sağ: sensör değerleri + durum
Anomali durumuna göre kenarlık rengi değişir.
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                                 QLabel, QSizePolicy)
from PySide6.QtCore    import Qt

from dashboard.styles        import C
from dashboard.widgets.energy_gauge import EnergyGauge
from dashboard.data_source   import NodeReading


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def _color_for_ph(ph: float) -> str:
    if ph < 4.5 or ph > 8.5: return "danger"
    if ph < 5.5 or ph > 7.5: return "warning"
    return "ok"

def _color_for_gas(gas: float) -> str:
    if gas > 400: return "danger"
    if gas > 250: return "warning"
    return "ok"

def _color_for_soil(sm: float) -> str:
    if sm < 10 or sm > 92: return "danger"
    if sm < 20 or sm > 80: return "warning"
    return "ok"

def _color_for_temp(tc: float) -> str:
    if tc > 40: return "danger"
    if tc > 35: return "warning"
    return "ok"

DECISION_ICONS = {
    "sleep":    ("●", C["TEXT_DIM"]),
    "measure":  ("◉", C["CYAN"]),
    "transmit": ("▲", C["ACCENT"]),
}


class _SensorRow(QFrame):
    """İkon + etiket + değer + birim içeren tek satır."""

    def __init__(self, icon: str, label: str, unit: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(6)

        self._icon = QLabel(icon)
        self._icon.setFixedWidth(16)
        self._icon.setStyleSheet(f"color: {C['TEXT_SEC']}; font-size:12px;")

        self._lbl = QLabel(label)
        self._lbl.setObjectName("sensorLabel")
        self._lbl.setFixedWidth(56)

        self._val = QLabel("—")
        self._val.setObjectName("sensorValue")
        self._val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._unit = QLabel(unit)
        self._unit.setFixedWidth(28)
        self._unit.setStyleSheet(f"color:{C['TEXT_DIM']}; font-size:10px;")

        layout.addWidget(self._icon)
        layout.addWidget(self._lbl)
        layout.addStretch()
        layout.addWidget(self._val)
        layout.addWidget(self._unit)

    def update_value(self, text: str, alert: str = "ok"):
        self._val.setText(text)
        self._val.setProperty("alert", alert)
        # Stil yenile
        self._val.style().unpolish(self._val)
        self._val.style().polish(self._val)


# ── Ana kart ──────────────────────────────────────────────────────────────────

class NodeCard(QFrame):
    """
    Tek sensör node'unu gösteren kart bileşeni.
    update(reading) ile canlı veriye güncellenir.
    """

    def __init__(self, node_id: int, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.setObjectName("nodeCard")
        self.setProperty("status", "normal")
        self.setMinimumWidth(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(6)

        # ── Başlık satırı ─────────────────────────────────────────────────
        header = QHBoxLayout()
        self._dot = QLabel("●")
        self._dot.setObjectName("cardOnlineDot")
        self._dot.setStyleSheet(f"color: {C['ACCENT']}; font-size:10px;")

        self._title = QLabel(f"NODE {self.node_id:02d}")
        self._title.setObjectName("cardNodeId")

        self._decision_lbl = QLabel("—")
        self._decision_lbl.setObjectName("cardDecision")
        self._decision_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header.addWidget(self._dot)
        header.addWidget(self._title)
        header.addStretch()
        header.addWidget(self._decision_lbl)
        outer.addLayout(header)

        # ── İçerik: gauge + sensörler ──────────────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(12)

        self._gauge = EnergyGauge(node_id=self.node_id)
        content.addWidget(self._gauge)

        # Sağ panel: sensör satırları
        sensor_panel = QVBoxLayout()
        sensor_panel.setSpacing(2)
        sensor_panel.setContentsMargins(0, 4, 0, 4)

        self._row_soil = _SensorRow("🌱", "Nem",  "%")
        self._row_temp = _SensorRow("🌡", "Sıcak","°C")
        self._row_ph   = _SensorRow("⚗", "pH",   "")
        self._row_gas  = _SensorRow("💨", "Gaz",  "ppm")

        for row in (self._row_soil, self._row_temp, self._row_ph, self._row_gas):
            sensor_panel.addWidget(row)

        sensor_panel.addStretch()

        # Zaman damgası
        self._ts_lbl = QLabel("—")
        self._ts_lbl.setStyleSheet(
            f"color:{C['TEXT_DIM']}; font-size:9px; letter-spacing:1px;")
        sensor_panel.addWidget(self._ts_lbl)

        content.addLayout(sensor_panel)
        outer.addLayout(content)

    # ── Güncelleme ────────────────────────────────────────────────────────────

    def update(self, r: NodeReading):
        # Enerji göstergesi
        is_tx = (r.decision == "transmit")
        self._gauge.setValue(r.soc, blinking=is_tx)

        # Karar göstergesi
        icon, color = DECISION_ICONS.get(r.decision, ("●", C["TEXT_DIM"]))
        self._decision_lbl.setText(f"{icon} {r.decision.upper()}")
        self._decision_lbl.setStyleSheet(
            f"color:{color}; font-size:10px; letter-spacing:1px;")

        # Sensör değerleri
        self._row_soil.update_value(f"{r.soil_moisture:.1f}", _color_for_soil(r.soil_moisture))
        self._row_temp.update_value(f"{r.temperature_c:.1f}", _color_for_temp(r.temperature_c))
        self._row_ph.update_value(  f"{r.ph:.2f}",            _color_for_ph(r.ph))
        self._row_gas.update_value( f"{r.gas_ppm:.0f}",       _color_for_gas(r.gas_ppm))

        # Zaman damgası
        self._ts_lbl.setText(f"⏱ {r.timestamp}")

        # Kart durumu → kenarlık rengi
        status = "normal"
        if not r.is_anomaly:
            pass
        elif r.gas_ppm > 400 or r.ph < 4.5 or r.ph > 8.5:
            status = "danger"
        else:
            status = "warning"

        self._dot.setStyleSheet(
            f"color: {C['ACCENT'] if status == 'normal' else C['WARNING'] if status == 'warning' else C['DANGER']};"
            f" font-size:10px;")

        if self.property("status") != status:
            self.setProperty("status", status)
            self.style().unpolish(self)
            self.style().polish(self)
