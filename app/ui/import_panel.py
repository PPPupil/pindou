"""图片与目标尺寸输入面板。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class ImportPanel(QWidget):
    convert_requested = Signal(str, int, int, str, int, str, int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.image_path = ""
        self.path_label = QLabel("尚未选择图片")
        self.path_label.setWordWrap(True)
        self.image_info_label = QLabel("图片尺寸：—")

        choose_button = QPushButton("选择图片")
        choose_button.clicked.connect(self._choose_image)

        self.width_input = QSpinBox()
        self.width_input.setRange(1, 500)
        self.width_input.setValue(50)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 500)
        self.height_input.setValue(50)

        size_form = QFormLayout()
        size_form.addRow("横向豆数", self.width_input)
        size_form.addRow("纵向豆数", self.height_input)

        self.keep_aspect_ratio = QCheckBox("保持原图比例（空余区域使用白色填充）")
        self.keep_aspect_ratio.setChecked(True)
        self.keep_aspect_ratio.setToolTip(
            "勾选后完整保留原图，不裁切；图片比例与拼豆画布不一致时用白色补齐。"
        )
        self.palette_level = QComboBox()
        for level in (24, 48, 72, 96, 120, 221):
            label = f"{level} 色完整色板" if level == 221 else f"{level} 色套装"
            self.palette_level.addItem(label, level)
        self.palette_level.setCurrentIndex(-1)
        self.palette_level.setPlaceholderText("未选择（自动判断）")
        self.palette_level.setToolTip(
            "不选择时自动判断：短边<30使用24色，30–49使用48色，"
            "50–99使用96色，短边≥100使用221色。"
        )
        size_form.addRow("色卡等级", self.palette_level)

        self.image_style = QComboBox()
        self.image_style.addItem("自动判断", "auto")
        self.image_style.addItem("卡通 / 图标", "cartoon")
        self.image_style.addItem("照片", "photo")
        self.image_style.setToolTip(
            "卡通模式会减少 JPEG 噪声和缩放过渡色，并清理 1～3 颗豆的小色块。"
        )
        size_form.addRow("图像类型", self.image_style)

        self.color_complexity = QComboBox()
        self.color_complexity.addItem("自动判断", 0)
        self.color_complexity.addItem("简单（最多 12 色）", 12)
        self.color_complexity.addItem("标准（最多 24 色）", 24)
        self.color_complexity.addItem("丰富（最多 48 色）", 48)
        self.color_complexity.addItem("自定义", -1)
        self.color_complexity.currentIndexChanged.connect(
            self._update_custom_color_limit
        )
        size_form.addRow("颜色复杂度", self.color_complexity)

        self.custom_color_limit = QSpinBox()
        self.custom_color_limit.setRange(2, 221)
        self.custom_color_limit.setValue(16)
        self.custom_color_limit.setEnabled(False)
        self.custom_color_limit.setToolTip("实际结果不会超过所选色卡中可用的颜色数量。")
        size_form.addRow("自定义用色上限", self.custom_color_limit)

        self.remove_outliers = QCheckBox("启用")
        self.remove_outliers.setChecked(True)
        self.remove_outliers.setToolTip(
            "只清理全图数量很少、与周围主色接近的格子；高反差眼睛和轮廓会保留。"
        )
        self.remove_outliers.toggled.connect(self._update_outlier_setting)
        size_form.addRow("消除异常色点", self.remove_outliers)

        self.outlier_max_count = QSpinBox()
        self.outlier_max_count.setRange(1, 5)
        self.outlier_max_count.setValue(1)
        self.outlier_max_count.setToolTip(
            "某色号在全图中的用量不超过该值时，才可能被判定为异常点。"
        )
        size_form.addRow("异常色最大用量", self.outlier_max_count)

        convert_button = QPushButton("生成拼豆图")
        convert_button.clicked.connect(self._request_conversion)

        choose_layout = QHBoxLayout()
        choose_layout.addWidget(choose_button)
        choose_layout.addWidget(self.path_label, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(choose_layout)
        layout.addWidget(self.image_info_label)
        layout.addLayout(size_form)
        layout.addWidget(self.keep_aspect_ratio)
        layout.addWidget(convert_button)

    def _choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if path:
            self.image_path = path
            self.path_label.setText(path)
            size = QImageReader(path).size()
            if size.isValid():
                ratio = size.width() / size.height()
                self.image_info_label.setText(
                    f"图片尺寸：{size.width()} × {size.height()}（比例 {ratio:.2f}:1）"
                )
            else:
                self.image_info_label.setText("图片尺寸：无法读取")

    def _request_conversion(self) -> None:
        if self.image_path:
            mode = "contain" if self.keep_aspect_ratio.isChecked() else "crop"
            selected_level = self.palette_level.currentData()
            selected_color_limit = int(self.color_complexity.currentData())
            if selected_color_limit == -1:
                selected_color_limit = self.custom_color_limit.value()
            self.convert_requested.emit(
                self.image_path,
                self.width_input.value(),
                self.height_input.value(),
                mode,
                int(selected_level) if selected_level is not None else 0,
                str(self.image_style.currentData()),
                selected_color_limit,
                self.outlier_max_count.value()
                if self.remove_outliers.isChecked()
                else 0,
            )

    def _update_custom_color_limit(self, _index: int = -1) -> None:
        self.custom_color_limit.setEnabled(self.color_complexity.currentData() == -1)

    def _update_outlier_setting(self, enabled: bool) -> None:
        self.outlier_max_count.setEnabled(enabled)
