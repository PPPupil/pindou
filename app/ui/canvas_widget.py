"""拼豆网格预览控件。"""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.core.project import BeadColor, BeadProject


class CanvasWidget(QWidget):
    BASE_CELL_SIZE = 16.0
    MIN_ZOOM = 5
    MAX_ZOOM = 400

    zoom_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project: BeadProject | None = None
        self.colors: dict[str, QColor] = {}
        self._zoom_percent = 100
        self.setMinimumSize(400, 400)

    @property
    def cell_size(self) -> float:
        return self.BASE_CELL_SIZE * self._zoom_percent / 100

    @property
    def zoom_percent(self) -> int:
        return self._zoom_percent

    def set_project(self, project: BeadProject, palette: list[BeadColor]) -> None:
        self.project = project
        self.colors = {color.code: QColor(*color.rgb) for color in palette}
        self._update_canvas_size()

    def set_zoom_percent(self, percent: int) -> None:
        bounded_percent = max(self.MIN_ZOOM, min(self.MAX_ZOOM, percent))
        if bounded_percent == self._zoom_percent:
            return
        self._zoom_percent = bounded_percent
        self._update_canvas_size()
        self.zoom_changed.emit(bounded_percent)

    def _update_canvas_size(self) -> None:
        if self.project:
            self.setFixedSize(
                math.ceil(self.project.width * self.cell_size),
                math.ceil(self.project.height * self.cell_size),
            )
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        if self.project:
            return QSize(
                math.ceil(self.project.width * self.cell_size),
                math.ceil(self.project.height * self.cell_size),
            )
        return QSize(600, 600)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        if not self.project:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "请选择图片并生成拼豆图")
            return

        show_grid = self.cell_size >= 4
        show_codes = self.cell_size >= 24
        painter.setPen(
            QPen(QColor(150, 150, 150), 1) if show_grid else Qt.PenStyle.NoPen
        )
        for y, row in enumerate(self.project.grid):
            for x, code in enumerate(row):
                rectangle = QRectF(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                bead_color = self.colors.get(code, QColor("magenta"))
                painter.fillRect(rectangle, bead_color)
                if show_grid:
                    painter.setPen(QPen(QColor(150, 150, 150), 1))
                    painter.drawRect(rectangle)
                if show_codes:
                    font = painter.font()
                    font.setPixelSize(max(8, int(self.cell_size * 0.32)))
                    painter.setFont(font)
                    painter.setPen(
                        QColor("black" if bead_color.lightness() > 150 else "white")
                    )
                    painter.drawText(rectangle, Qt.AlignmentFlag.AlignCenter, code)

    def wheelEvent(self, event) -> None:  # noqa: N802
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            step = 10 if event.angleDelta().y() > 0 else -10
            self.set_zoom_percent(self._zoom_percent + step)
            event.accept()
            return
        super().wheelEvent(event)
