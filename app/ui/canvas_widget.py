"""拼豆网格预览控件。"""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.core.project import BeadColor, BeadProject


class CanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project: BeadProject | None = None
        self.colors: dict[str, QColor] = {}
        self.cell_size = 16
        self.setMinimumSize(400, 400)

    def set_project(self, project: BeadProject, palette: list[BeadColor]) -> None:
        self.project = project
        self.colors = {color.code: QColor(*color.rgb) for color in palette}
        self.setMinimumSize(project.width * self.cell_size, project.height * self.cell_size)
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        if self.project:
            return QSize(
                self.project.width * self.cell_size,
                self.project.height * self.cell_size,
            )
        return QSize(600, 600)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        if not self.project:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "请选择图片并生成拼豆图")
            return

        painter.setPen(QPen(QColor(150, 150, 150), 1))
        for y, row in enumerate(self.project.grid):
            for x, code in enumerate(row):
                rectangle = QRect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                painter.fillRect(rectangle, self.colors.get(code, QColor("magenta")))
                painter.drawRect(rectangle)

