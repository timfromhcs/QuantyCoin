"""
QuantyCoin Native Qt Real-Time Dynamic Graph Widget (v4.0)
Inspired by Bitcoin Core / Bitcoin Cash II trafficgraphwidget.cpp
Provides hardware-accelerated QPainter real-time curve rendering with grid lines and gradients.
"""

from typing import List, Tuple, Optional
from PySide6 import QtWidgets, QtCore, QtGui


class RealTimeGraphWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, title: str = "Real-Time Telemetry", unit: str = "kH/s", color: str = "#00F0FF"):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.color = QtGui.QColor(color)
        self.history: List[float] = [0.0] * 60
        self.setMinimumHeight(140)
        self.setMinimumWidth(280)
        self.max_val: float = 10.0

    def add_sample(self, value: float):
        self.history.pop(0)
        self.history.append(float(value))
        peak = max(self.history)
        self.max_val = max(peak * 1.25, 1.0)
        self.update()

    def set_samples(self, samples: List[float]):
        if samples:
            self.history = list(samples)[-60:]
            if len(self.history) < 60:
                self.history = [0.0] * (60 - len(self.history)) + self.history
            peak = max(self.history)
            self.max_val = max(peak * 1.25, 1.0)
            self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QtGui.QColor("#0E121A"))

        # Outer border
        painter.setPen(QtGui.QPen(QtGui.QColor("#1E293B"), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        # Grid lines
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 15), 1, QtCore.Qt.PenStyle.DashLine))
        for y_step in range(1, 4):
            y_pos = int(h * y_step / 4)
            painter.drawLine(0, y_pos, w, y_pos)

        # Data Curve
        if len(self.history) >= 2:
            step = w / (len(self.history) - 1)
            points: List[QtCore.QPointF] = []
            for i, val in enumerate(self.history):
                x = i * step
                y = h - (val / self.max_val) * (h - 24) - 6
                points.append(QtCore.QPointF(x, y))

            # Filled Gradient Polygon
            path = QtGui.QPainterPath()
            path.moveTo(0, h)
            for pt in points:
                path.lineTo(pt)
            path.lineTo(w, h)
            path.closeSubpath()

            grad = QtGui.QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 90))
            grad.setColorAt(1, QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 5))
            painter.fillPath(path, grad)

            # Stroke line
            pen = QtGui.QPen(self.color, 2)
            painter.setPen(pen)
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

        # Header Title & Max Scale
        painter.setPen(QtGui.QColor("#94A3B8"))
        painter.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Weight.Bold))
        painter.drawText(10, 16, self.title)

        latest = self.history[-1] if self.history else 0.0
        val_text = f"{latest:.2f} {self.unit}"
        painter.setPen(self.color)
        painter.setFont(QtGui.QFont("JetBrains Mono", 10, QtGui.QFont.Weight.Bold))
        painter.drawText(w - 120, 16, val_text)
