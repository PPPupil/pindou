"""应用主窗口与界面模块编排。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.converter import BeadConverter
from app.core.project import BeadProject
from app.services.exporter import export_png
from app.services.palette_loader import Palette, load_palette
from app.ui.canvas_widget import CanvasWidget
from app.ui.import_panel import ImportPanel
from app.ui.palette_panel import PalettePanel
from app.ui.statistics_panel import StatisticsPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("拼豆图生成器")
        self.resize(1100, 750)

        palette_path = (
            Path(__file__).resolve().parents[1] / "resources" / "palettes" / "default.json"
        )
        self.palette: Palette = load_palette(palette_path)
        self.project: BeadProject | None = None

        self.import_panel = ImportPanel()
        self.import_panel.convert_requested.connect(self._convert_image)
        self.canvas = CanvasWidget()
        self.palette_panel = PalettePanel()
        self.palette_panel.set_palette(self.palette.colors)
        self.statistics_panel = StatisticsPanel()

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(False)

        tabs = QTabWidget()
        tabs.addTab(self.palette_panel, "色板")
        tabs.addTab(self.statistics_panel, "用量")

        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.addWidget(self.import_panel)
        side_layout.addWidget(tabs, 1)

        splitter = QSplitter()
        splitter.addWidget(side_panel)
        splitter.addWidget(scroll_area)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        export_action = self.menuBar().addAction("导出 PNG")
        export_action.triggered.connect(self._export_png)
        self.statusBar().showMessage(f"当前色板：{self.palette.brand}")

    def _convert_image(self, image_path: str, width: int, height: int) -> None:
        try:
            converter = BeadConverter(self.palette.colors, self.palette.brand)
            self.project = converter.convert(image_path, width, height)
            self.canvas.set_project(self.project, self.palette.colors)
            self.statistics_panel.set_project(self.project, self.palette.colors)
            self.statusBar().showMessage(f"已生成 {width} × {height}，共 {width * height} 颗豆")
        except Exception as error:  # UI 边界统一显示可读错误
            QMessageBox.critical(self, "生成失败", str(error))

    def _export_png(self) -> None:
        if self.project is None:
            QMessageBox.information(self, "尚无作品", "请先选择图片并生成拼豆图。")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出拼豆示意图",
            "拼豆示意图.png",
            "PNG 图片 (*.png)",
        )
        if not path:
            return
        try:
            export_png(self.project, self.palette.colors, path)
            self.statusBar().showMessage(f"已导出：{path}")
        except Exception as error:
            QMessageBox.critical(self, "导出失败", str(error))

