"""拼豆网格预览控件。"""

from __future__ import annotations

import math

from PySide6.QtCore import QLineF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.core.grid_guides import coordinate_marks, is_major_grid_line
from app.core.project import BeadColor, BeadProject


class CanvasWidget(QWidget):
    BASE_CELL_SIZE = 16.0
    MIN_ZOOM = 5
    MAX_ZOOM = 400
    MIN_COORDINATE_MARGIN = 22.0
    MAX_COORDINATE_MARGIN = 42.0

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

    @property
    def coordinate_margin(self) -> float:
        return max(
            self.MIN_COORDINATE_MARGIN,
            min(self.MAX_COORDINATE_MARGIN, self.cell_size * 2),
        )

    def _canvas_size(self) -> QSize:
        if not self.project:
            return QSize(600, 600)
        margin = self.coordinate_margin
        return QSize(
            math.ceil(self.project.width * self.cell_size + margin * 2),
            math.ceil(self.project.height * self.cell_size + margin * 2),
        )

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
            self.setFixedSize(self._canvas_size())
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        if self.project:
            return self._canvas_size()
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
        margin = self.coordinate_margin
        grid_width = self.project.width * self.cell_size
        grid_height = self.project.height * self.cell_size
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for y, row in enumerate(self.project.grid):
            for x, code in enumerate(row):
                rectangle = QRectF(
                    margin + x * self.cell_size,
                    margin + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                bead_color = self.colors.get(code, QColor("magenta"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(bead_color)
                painter.drawEllipse(rectangle)
                if show_codes:
                    font = painter.font()
                    font.setPixelSize(max(8, int(self.cell_size * 0.32)))
                    painter.setFont(font)
                    painter.setPen(
                        QColor("black" if bead_color.lightness() > 150 else "white")
                    )
                    painter.drawText(rectangle, Qt.AlignmentFlag.AlignCenter, code)

        if show_grid:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            regular_pen = QPen(QColor(155, 155, 155), 1)
            major_pen = QPen(
                QColor(55, 55, 55),
                max(2.0, min(4.0, self.cell_size * 0.12)),
            )
            for line_index in range(self.project.width + 1):
                painter.setPen(
                    major_pen
                    if is_major_grid_line(line_index, self.project.width)
                    else regular_pen
                )
                x = margin + line_index * self.cell_size
                painter.drawLine(QLineF(x, margin, x, margin + grid_height))
            for line_index in range(self.project.height + 1):
                painter.setPen(
                    major_pen
                    if is_major_grid_line(line_index, self.project.height)
                    else regular_pen
                )
                y = margin + line_index * self.cell_size
                painter.drawLine(QLineF(margin, y, margin + grid_width, y))

            coordinate_font = painter.font()
            coordinate_font.setBold(True)
            coordinate_font.setPixelSize(
                max(8, min(14, int(self.cell_size * 0.7)))
            )
            painter.setFont(coordinate_font)
            painter.setPen(QColor(45, 45, 45))
            horizontal_label_width = max(28.0, self.cell_size * 4)
            vertical_label_height = max(18.0, self.cell_size * 1.5)
            for coordinate in coordinate_marks(self.project.width):
                center_x = margin + (coordinate - 0.5) * self.cell_size
                top_rect = QRectF(
                    center_x - horizontal_label_width / 2,
                    0,
                    horizontal_label_width,
                    margin,
                )
                bottom_rect = QRectF(
                    center_x - horizontal_label_width / 2,
                    margin + grid_height,
                    horizontal_label_width,
                    margin,
                )
                painter.drawText(top_rect, Qt.AlignmentFlag.AlignCenter, str(coordinate))
                painter.drawText(
                    bottom_rect,
                    Qt.AlignmentFlag.AlignCenter,
                    str(coordinate),
                )

            for coordinate in coordinate_marks(self.project.height):
                center_y = margin + (coordinate - 0.5) * self.cell_size
                left_rect = QRectF(
                    0,
                    center_y - vertical_label_height / 2,
                    margin,
                    vertical_label_height,
                )
                right_rect = QRectF(
                    margin + grid_width,
                    center_y - vertical_label_height / 2,
                    margin,
                    vertical_label_height,
                )
                painter.drawText(left_rect, Qt.AlignmentFlag.AlignCenter, str(coordinate))
                painter.drawText(
                    right_rect,
                    Qt.AlignmentFlag.AlignCenter,
                    str(coordinate),
                )

    def wheelEvent(self, event) -> None:  # noqa: N802
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            step = 10 if event.angleDelta().y() > 0 else -10
            self.set_zoom_percent(self._zoom_percent + step)
            event.accept()
            return
        super().wheelEvent(event)
