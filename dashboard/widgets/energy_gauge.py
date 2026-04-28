"""
EnergyGauge — Dairesel MFC enerji göstergesi
QPainter ile çizilir; biyolüminesans renk geçişi ve glow efekti içerir.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore    import Qt, QRectF, QTimer
from PySide6.QtGui     import (QPainter, QPen, QColor, QFont,
                                QRadialGradient, QConicalGradient)

from dashboard.styles import C


class EnergyGauge(QWidget):
    """
    0.0–1.0 arası SOC değeri için dairesel gösterge.
    setValue() çağrıldığında yumuşak animasyonla hedef değere kayar.
    """

    def __init__(self, node_id: int = 1, parent=None):
        super().__init__(parent)
        self.node_id  = node_id
        self._value   = 0.0    # anlık gösterilen değer
        self._target  = 0.0    # hedef değer
        self._blink   = False  # TX sırasında yanıp söner
        self._blink_on = False

        self.setMinimumSize(140, 140)
        self.setMaximumSize(180, 180)

        # Animasyon zamanlayıcısı
        self._anim = QTimer(self)
        self._anim.setInterval(30)   # ~33 fps
        self._anim.timeout.connect(self._animate)
        self._anim.start()

    def setValue(self, soc: float, blinking: bool = False):
        self._target = max(0.0, min(1.0, soc))
        self._blink  = blinking

    def _animate(self):
        # Yumuşak interpolasyon
        diff = self._target - self._value
        if abs(diff) > 0.001:
            self._value += diff * 0.12
            self.update()

        # Blink döngüsü (TX)
        if self._blink:
            self._blink_on = not self._blink_on
            self.update()

    # ── Renk mantığı ─────────────────────────────────────────────────────────

    def _arc_color(self) -> QColor:
        v = self._value
        if v > 0.65:
            return QColor(C["ACCENT"])
        if v > 0.35:
            return QColor(C["WARNING"])
        return QColor(C["DANGER"])

    # ── Çizim ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W, H  = self.width(), self.height()
        size  = min(W, H) - 24
        cx, cy = W / 2, H / 2

        # ── Arkaplan dairesi ─────────────────────────────────────────────────
        p.setPen(Qt.NoPen)
        grad = QRadialGradient(cx, cy, size / 2)
        grad.setColorAt(0.0, QColor("#142030"))
        grad.setColorAt(1.0, QColor(C["BG_DEEP"]))
        p.setBrush(grad)
        p.drawEllipse(int(cx - size/2), int(cy - size/2), size, size)

        rect = QRectF(cx - size/2 + 14, cy - size/2 + 14, size - 28, size - 28)
        START_ANGLE = 225   # derece
        SWEEP       = 270

        # ── Ray (iz izi) ─────────────────────────────────────────────────────
        pen = QPen(QColor(C["BORDER"]), 10)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawArc(rect, START_ANGLE * 16, -SWEEP * 16)

        # ── Değer yayı ───────────────────────────────────────────────────────
        arc_color = self._arc_color()
        span = int(-SWEEP * 16 * self._value)

        # Glow (hafif dış parlama)
        glow = QColor(arc_color)
        glow.setAlpha(35)
        pen_glow = QPen(glow, 18)
        pen_glow.setCapStyle(Qt.RoundCap)
        p.setPen(pen_glow)
        p.drawArc(rect, START_ANGLE * 16, span)

        # Ana yay
        pen_main = QPen(arc_color, 10)
        pen_main.setCapStyle(Qt.RoundCap)
        p.setPen(pen_main)
        p.drawArc(rect, START_ANGLE * 16, span)

        # ── İbre ucu noktası ─────────────────────────────────────────────────
        if self._value > 0.02:
            angle_rad = math.radians(START_ANGLE - SWEEP * self._value)
            r = (size - 28) / 2
            tip_x = cx + r * math.cos(angle_rad)
            tip_y = cy - r * math.sin(angle_rad)
            p.setBrush(arc_color)
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(tip_x - 5), int(tip_y - 5), 10, 10)

        # ── Merkez yüzdesi ───────────────────────────────────────────────────
        # TX blink
        if self._blink and self._blink_on:
            p.setPen(QColor(C["CYAN"]))
            font = QFont("Consolas", int(size * 0.13), QFont.Bold)
            p.setFont(font)
            p.drawText(QRectF(cx - size/2, cy - size/3.5, size, size/2.5),
                       Qt.AlignCenter, "TX ↑")
        else:
            p.setPen(QColor(C["TEXT_PRI"]))
            font = QFont("Consolas", int(size * 0.15), QFont.Bold)
            p.setFont(font)
            p.drawText(QRectF(cx - size/2, cy - size/3.5, size, size/2.5),
                       Qt.AlignCenter, f"{int(self._value * 100)}%")

        # ── Node etiketi ─────────────────────────────────────────────────────
        p.setPen(QColor(C["TEXT_SEC"]))
        font2 = QFont("Consolas", int(size * 0.075))
        p.setFont(font2)
        p.drawText(QRectF(cx - size/2, cy + size/10, size, size/4),
                   Qt.AlignCenter, "MFC ENERJİ")

        p.end()
