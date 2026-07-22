"""各颜色用量统计面板。"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.core.project import BeadColor, BeadProject, color_code_sort_key


class StatisticsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.total_label = QLabel("总豆数：0")
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["色号", "中文名称", "数量"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.total_label)
        layout.addWidget(self.table)

    def set_project(self, project: BeadProject, palette: list[BeadColor]) -> None:
        counts = project.color_counts()
        colors = {color.code: color for color in palette}
        items = sorted(counts.items(), key=lambda item: color_code_sort_key(item[0]))

        self.total_label.setText(f"总豆数：{project.total_beads}")
        self.table.setRowCount(len(items))
        for row, (code, count) in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(code))
            color = colors.get(code)
            name_item = QTableWidgetItem(color.name if color else "未知")
            if color:
                name_item.setBackground(QColor(*color.rgb))
                brightness = (
                    0.299 * color.rgb[0]
                    + 0.587 * color.rgb[1]
                    + 0.114 * color.rgb[2]
                )
                name_item.setForeground(QColor("black" if brightness > 150 else "white"))
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, QTableWidgetItem(str(count)))
        self.table.resizeColumnsToContents()

