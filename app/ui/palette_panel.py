"""色板信息面板。"""

from __future__ import annotations

from collections.abc import Collection

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.core.project import color_code_sort_key
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

    def set_palette(
        self,
        palette: Palette,
        used_codes: Collection[str] = (),
    ) -> None:
        used_code_set = set(used_codes)
        visible_colors = sorted(
            (color for color in palette.colors if color.code in used_code_set),
            key=lambda color: color_code_sort_key(color.code),
        )
        self.info_label.setText(
            f"当前作品使用 {len(visible_colors)} 种颜色\n"
            "按色号 A–Z、0–9 自然排序"
        )
        self.info_label.setToolTip(
            "\n".join([f"来源：{palette.source or '未说明'}", *palette.notes])
        )
        self.list_widget.clear()
        for color in visible_colors:
            item = QListWidgetItem(f"{color.code}  {color.name}")
            item.setBackground(QColor(*color.rgb))
            item.setForeground(self._text_color(color.rgb))
            self.list_widget.addItem(item)

    @staticmethod
    def _text_color(rgb: tuple[int, int, int]) -> QColor:
        brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        return QColor("black" if brightness > 150 else "white")

