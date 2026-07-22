"""各颜色用量统计面板。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.core.project import BeadColor, BeadProject


class StatisticsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.total_label = QLabel("总豆数：0")
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["编号", "颜色", "数量"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.total_label)
        layout.addWidget(self.table)

    def set_project(self, project: BeadProject, palette: list[BeadColor]) -> None:
        counts = project.color_counts()
        names = {color.code: color.name for color in palette}
        items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

        self.total_label.setText(f"总豆数：{project.total_beads}")
        self.table.setRowCount(len(items))
        for row, (code, count) in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(names.get(code, "未知")))
            self.table.setItem(row, 2, QTableWidgetItem(str(count)))
        self.table.resizeColumnsToContents()

