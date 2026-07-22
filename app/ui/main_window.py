"""应用主窗口与界面模块编排。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.converter import BeadConverter
from app.core.image_processor import ResizeMode
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

        project_root = Path(__file__).resolve().parents[2]
        marketplace_palette = project_root / "mard_221_approx_from_chart.json"
        fallback_palette = (
            Path(__file__).resolve().parents[1] / "resources" / "palettes" / "default.json"
        )
        palette_path = marketplace_palette if marketplace_palette.exists() else fallback_palette
        self.palette: Palette = load_palette(palette_path)
        self.project: BeadProject | None = None

        self.import_panel = ImportPanel()
        self.import_panel.convert_requested.connect(self._convert_image)
        self.canvas = CanvasWidget()
        self.palette_panel = PalettePanel()
        self.palette_panel.set_palette(self.palette)
        self.statistics_panel = StatisticsPanel()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        zoom_out_button = QPushButton("−")
        zoom_out_button.setToolTip("缩小预览")
        zoom_out_button.clicked.connect(lambda: self._step_zoom(-10))
        zoom_in_button = QPushButton("+")
        zoom_in_button.setToolTip("放大预览")
        zoom_in_button.clicked.connect(lambda: self._step_zoom(10))
        fit_button = QPushButton("适应窗口")
        fit_button.setToolTip("自动缩放，以显示完整拼豆图")
        fit_button.clicked.connect(self._fit_preview)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(CanvasWidget.MIN_ZOOM, CanvasWidget.MAX_ZOOM)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setToolTip("也可以按住 Ctrl 并滚动鼠标滚轮缩放")
        self.zoom_slider.valueChanged.connect(self.canvas.set_zoom_percent)
        self.zoom_label = QLabel("100%")
        self.zoom_slider.valueChanged.connect(
            lambda value: self.zoom_label.setText(f"{value}%")
        )
        self.canvas.zoom_changed.connect(self.zoom_slider.setValue)

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("预览缩放"))
        zoom_layout.addWidget(zoom_out_button)
        zoom_layout.addWidget(self.zoom_slider, 1)
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(fit_button)

        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addLayout(zoom_layout)
        preview_layout.addWidget(self.scroll_area, 1)

        tabs = QTabWidget()
        tabs.addTab(self.palette_panel, "色板")
        tabs.addTab(self.statistics_panel, "用量")

        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.addWidget(self.import_panel)
        side_layout.addWidget(tabs, 1)

        splitter = QSplitter()
        splitter.addWidget(side_panel)
        splitter.addWidget(preview_panel)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        export_action = self.menuBar().addAction("导出 PNG")
        export_action.triggered.connect(self._export_png)
        self.statusBar().showMessage(
            f"当前色板：{self.palette.brand}（{len(self.palette.colors)} 色）"
        )

    def _convert_image(
        self,
        image_path: str,
        width: int,
        height: int,
        mode: ResizeMode,
    ) -> None:
        try:
            converter = BeadConverter(self.palette.colors, self.palette.brand)
            self.project = converter.convert(image_path, width, height, mode)
            self.canvas.set_project(self.project, self.palette.colors)
            self.statistics_panel.set_project(self.project, self.palette.colors)
            QTimer.singleShot(0, self._fit_preview)
            mode_text = "保持比例并补白" if mode == "contain" else "居中裁切"
            self.statusBar().showMessage(
                f"已生成 {width} × {height}，共 {width * height} 颗豆（{mode_text}）"
            )
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

    def _step_zoom(self, step: int) -> None:
        self.zoom_slider.setValue(self.zoom_slider.value() + step)

    def _fit_preview(self) -> None:
        if self.project is None:
            return
        viewport = self.scroll_area.viewport().size()
        horizontal_ratio = viewport.width() / (
            self.project.width * CanvasWidget.BASE_CELL_SIZE
        )
        vertical_ratio = viewport.height() / (
            self.project.height * CanvasWidget.BASE_CELL_SIZE
        )
        zoom_percent = int(min(horizontal_ratio, vertical_ratio) * 100)
        self.zoom_slider.setValue(
            max(
                self.zoom_slider.minimum(),
                min(self.zoom_slider.maximum(), zoom_percent),
            )
        )
