"""
Mikrobiyal AIoT Dashboard — Ana Pencere
========================================
Çalıştır:
    python dashboard/app.py
    python dashboard/app.py --nodes 4 --interval 800

Bağımlılıklar:
    pip install PySide6 pyqtgraph numpy scikit-learn
"""

import sys
import os
import argparse
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore    import Qt, QTimer
from PySide6.QtGui     import QFont, QPainter, QColor, QPen

# Kök dizini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dashboard.styles       import C, QSS
from dashboard.data_source  import DataSource
from dashboard.widgets.node_card    import NodeCard
from dashboard.widgets.chart_panel  import ChartPanel
from dashboard.widgets.anomaly_log  import AnomalyLog


# ── Arka plan çizim widget'ı (hex grid) ──────────────────────────────────────

class _HexBackground(QWidget):
    """Sayfanın arkasında biyolüminesans altıgen ızgarası çizer."""

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        size   = 28   # altıgen yarı çapı
        pen    = QPen(QColor(C["GRID"]), 1)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)

        import math
        col_w = size * 2
        row_h = size * math.sqrt(3)

        cols = int(self.width()  / col_w) + 3
        rows = int(self.height() / row_h) + 3

        for row in range(-1, rows):
            for col in range(-1, cols):
                cx = col * col_w * 1.5
                cy = row * row_h + (col % 2) * row_h / 2
                pts = []
                for k in range(6):
                    angle = math.radians(60 * k)
                    pts.append((cx + size * math.cos(angle),
                                cy + size * math.sin(angle)))
                from PySide6.QtGui import QPolygonF
                from PySide6.QtCore import QPointF
                poly = QPolygonF([QPointF(x, y) for x, y in pts])
                p.drawPolygon(poly)
        p.end()


# ── Header ───────────────────────────────────────────────────────────────────

class _Header(QFrame):
    def __init__(self, n_nodes: int, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(58)
        self.n_nodes = n_nodes

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        # Logo + başlık
        left = QVBoxLayout()
        left.setSpacing(0)
        title = QLabel("🌿  MİKROBİYAL AIoT DASHBOARD")
        title.setObjectName("appTitle")
        sub   = QLabel("MFC ENERJİ HASADI · OTONOM ÇEVRE SENSÖR AĞI")
        sub.setObjectName("appSubtitle")
        left.addWidget(title)
        left.addWidget(sub)
        layout.addLayout(left)
        layout.addStretch()

        # Node sayısı
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.setSpacing(2)

        self._node_lbl = QLabel(f"●  {n_nodes}/{n_nodes} NODE  ONLINE")
        self._node_lbl.setObjectName("nodeCountLabel")
        self._node_lbl.setStyleSheet(f"color:{C['ACCENT']}; font-size:11px;")
        self._node_lbl.setAlignment(Qt.AlignRight)

        self._clock = QLabel("—")
        self._clock.setObjectName("clockLabel")
        self._clock.setAlignment(Qt.AlignRight)

        right.addWidget(self._node_lbl)
        right.addWidget(self._clock)
        layout.addLayout(right)

    def tick(self, online: int):
        self._clock.setText(datetime.now().strftime("%H:%M:%S"))
        color = C["ACCENT"] if online == self.n_nodes else C["WARNING"]
        self._node_lbl.setText(f"●  {online}/{self.n_nodes} NODE  ONLINE")
        self._node_lbl.setStyleSheet(f"color:{color}; font-size:11px;")


# ── Bölüm başlığı ─────────────────────────────────────────────────────────────

def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("sectionTitle")
    return lbl


# ── Ana Pencere ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self, n_nodes: int = 3, interval_ms: int = 1000):
        super().__init__()
        self.setWindowTitle("Mikrobiyal AIoT Dashboard")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        # Veri kaynağı
        self.ds = DataSource(n_nodes=n_nodes, interval_ms=interval_ms)
        self.ds.start()

        # İlk tick — widget'lar hazır olmadan önce veriyi doldur
        self.ds.tick()

        self._build_ui(n_nodes)
        self._setup_timer(interval_ms)

    # ── UI inşası ─────────────────────────────────────────────────────────────

    def _build_ui(self, n_nodes: int):
        # Hex arka plan
        bg = _HexBackground(self)
        bg.setGeometry(0, 0, self.width(), self.height())
        bg.lower()

        # Merkez widget
        center = QWidget()
        self.setCentralWidget(center)
        root = QVBoxLayout(center)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        self._header = _Header(n_nodes=n_nodes)
        root.addWidget(self._header)

        # ── Gövde ─────────────────────────────────────────────────────────
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 12, 16, 12)
        body_layout.setSpacing(12)

        # ── Node kartları ──────────────────────────────────────────────────
        body_layout.addWidget(_section_title("SENSOR NODES"))

        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setFrameShape(QFrame.NoFrame)
        cards_scroll.setFixedHeight(265)
        cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        cards_widget = QWidget()
        self._cards_row = QHBoxLayout(cards_widget)
        self._cards_row.setContentsMargins(0, 0, 0, 4)
        self._cards_row.setSpacing(12)

        self._cards: list[NodeCard] = []
        for i in range(n_nodes):
            card = NodeCard(node_id=i + 1)
            self._cards.append(card)
            self._cards_row.addWidget(card)

        self._cards_row.addStretch()
        cards_scroll.setWidget(cards_widget)
        body_layout.addWidget(cards_scroll)

        # ── Alt panel: grafik + anomali logu ──────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # Sol: Grafik
        chart_col = QVBoxLayout()
        chart_col.addWidget(_section_title("CANLI GRAFİK"))
        self._chart = ChartPanel(data_source=self.ds, n_nodes=n_nodes)
        self._chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_col.addWidget(self._chart)
        bottom.addLayout(chart_col, stretch=3)

        # Sağ: Anomali logu
        log_col = QVBoxLayout()
        log_col.addWidget(_section_title("UYARILAR"))
        self._anomaly_log = AnomalyLog()
        self._anomaly_log.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._anomaly_log.setMinimumWidth(240)
        self._anomaly_log.setMaximumWidth(320)
        log_col.addWidget(self._anomaly_log)
        bottom.addLayout(log_col, stretch=1)

        body_layout.addLayout(bottom)

        # Scroll area ile gövdeyi sar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(body)
        root.addWidget(scroll)

    # ── Zamanlayıcı ───────────────────────────────────────────────────────────

    def _setup_timer(self, interval_ms: int):
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._refresh)
        self._timer.start()

    # ── Güncelleme döngüsü ────────────────────────────────────────────────────

    def _refresh(self):
        readings = self.ds.latest()
        if not readings:
            return

        # Node kartlarını güncelle
        for r in readings:
            idx = r.node_id - 1
            if 0 <= idx < len(self._cards):
                self._cards[idx].update(r)

        # Header
        online = sum(1 for r in readings if r.is_anomaly is not None)
        self._header.tick(online=len(readings))

        # Grafik
        self._chart.refresh()

        # Anomali logu
        self._anomaly_log.refresh(self.ds.anomalies())

    # ── Pencere yeniden boyutlanınca hex arka planı güncelle ──────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for child in self.findChildren(_HexBackground):
            child.setGeometry(0, 0, self.width(), self.height())

    def closeEvent(self, event):
        self.ds.stop()
        super().closeEvent(event)


# ── Giriş noktası ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Mikrobiyal AIoT Dashboard")
    parser.add_argument("--nodes",    type=int, default=3,    help="Node sayısı")
    parser.add_argument("--interval", type=int, default=1000, help="Güncelleme (ms)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("Mikrobiyal AIoT")
    app.setStyleSheet(QSS)

    font = QFont("Consolas", 11)
    app.setFont(font)

    win = MainWindow(n_nodes=args.nodes, interval_ms=args.interval)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
