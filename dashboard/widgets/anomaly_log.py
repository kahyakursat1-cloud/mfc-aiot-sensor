"""
AnomalyLog — Kaydırmalı anomali uyarı paneli.
En yeni uyarılar üstte gösterilir, anomali tipine göre renklendirilir.
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QListWidget,
                                 QListWidgetItem, QLabel)
from PySide6.QtCore    import Qt
from PySide6.QtGui     import QColor, QFont

from dashboard.styles import C


ANOMALY_COLORS = {
    "kuraklık":        C["WARNING"],
    "su baskını":      C["CYAN"],
    "yüksek sıcaklık": C["WARNING"],
    "pH düşük":        C["DANGER"],
    "pH yüksek":       C["DANGER"],
    "gaz sızıntısı":   C["DANGER"],
}

ANOMALY_ICONS = {
    "kuraklık":        "🌵",
    "su baskını":      "🌊",
    "yüksek sıcaklık": "🔥",
    "pH düşük":        "⚗",
    "pH yüksek":       "⚗",
    "gaz sızıntısı":   "☣",
}


class AnomalyLog(QFrame):
    """
    Anomali kayıtlarını listeler.
    refresh(events) ile güncellenir; events = DataSource.anomalies() çıktısı.
    """

    MAX_ITEMS = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("anomalyLog")
        self._build_ui()
        self._seen_keys: set = set()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Başlık
        title_row = QLabel("🚨  ANOMALİ KAYITLARI")
        title_row.setObjectName("anomalyTitle")
        layout.addWidget(title_row)

        # Boş durum etiketi
        self._empty_lbl = QLabel("  Anomali yok ✓")
        self._empty_lbl.setStyleSheet(
            f"color:{C['ACCENT_DIM']}; font-size:11px; padding:12px;")
        layout.addWidget(self._empty_lbl)

        # Liste
        self._list = QListWidget()
        self._list.setWordWrap(False)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setSpacing(1)
        font = QFont("Consolas", 10)
        self._list.setFont(font)
        layout.addWidget(self._list)
        self._list.hide()

    def refresh(self, events: list[dict]):
        if not events:
            self._empty_lbl.show()
            self._list.hide()
            return

        self._empty_lbl.hide()
        self._list.show()

        # Yeni anomaliler varsa başa ekle
        for ev in events:
            key = f"{ev['node']}-{ev['time']}-{ev['type']}"
            if key in self._seen_keys:
                continue
            self._seen_keys.add(key)

            atype  = ev["type"]
            color  = ANOMALY_COLORS.get(atype, C["TEXT_SEC"])
            icon   = ANOMALY_ICONS.get(atype,  "⚠")
            detail = self._detail(ev)

            text = f" {icon}  Node {ev['node']}  ·  {ev['time']}\n    {atype}  {detail}"
            item = QListWidgetItem(text)
            item.setForeground(QColor(color))
            item.setBackground(QColor("#0d1a24"))

            self._list.insertItem(0, item)

            # Limit
            while self._list.count() > self.MAX_ITEMS:
                self._list.takeItem(self._list.count() - 1)

    @staticmethod
    def _detail(ev: dict) -> str:
        parts = []
        if ev.get("soil")  is not None: parts.append(f"nem:{ev['soil']:.0f}%")
        if ev.get("ph")    is not None: parts.append(f"pH:{ev['ph']:.1f}")
        if ev.get("gas")   is not None and ev["gas"] > 0:
            parts.append(f"gaz:{ev['gas']:.0f}ppm")
        return "  ".join(parts)
