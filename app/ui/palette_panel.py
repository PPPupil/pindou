"""色板信息面板。"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.core.project import BeadColor


class PalettePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.list_widget = QListWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list_widget)

    def set_palette(self, colors: list[BeadColor]) -> None:
        self.list_widget.clear()
        for color in colors:
            item = QListWidgetItem(f"{color.code}  {color.name}")
            item.setBackground(QColor(*color.rgb))
            item.setForeground(self._text_color(color.rgb))
            self.list_widget.addItem(item)

    @staticmethod
    def _text_color(rgb: tuple[int, int, int]) -> QColor:
        brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        return QColor("black" if brightness > 150 else "white")

