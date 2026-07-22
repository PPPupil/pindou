"""色板信息面板。"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.services.palette_loader import Palette


class PalettePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.list_widget = QListWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.info_label)
        layout.addWidget(self.list_widget)

    def set_palette(self, palette: Palette) -> None:
        accuracy = palette.accuracy or "未说明"
        self.info_label.setText(
            f"{palette.brand}\n{len(palette.colors)} 色｜{palette.color_space}｜精度：{accuracy}"
        )
        self.info_label.setToolTip(
            "\n".join([f"来源：{palette.source or '未说明'}", *palette.notes])
        )
        self.list_widget.clear()
        for color in palette.colors:
            position = ""
            if color.source_row is not None and color.source_column is not None:
                position = f"  [{color.source_row},{color.source_column}]"
            transparent = "  透明" if color.transparent else ""
            name = f"  {color.name}" if color.name != color.code else ""
            item = QListWidgetItem(
                f"{color.code}  {color.hex_value}{name}{position}{transparent}"
            )
            if color.note:
                item.setToolTip(color.note)
            item.setBackground(QColor(*color.rgb))
            item.setForeground(self._text_color(color.rgb))
            self.list_widget.addItem(item)

    @staticmethod
    def _text_color(rgb: tuple[int, int, int]) -> QColor:
        brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        return QColor("black" if brightness > 150 else "white")

