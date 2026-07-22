"""图片与目标尺寸输入面板。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import (
    QCheckBox,
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
    convert_requested = Signal(str, int, int, str)

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
            self.convert_requested.emit(
                self.image_path,
                self.width_input.value(),
                self.height_input.value(),
                mode,
            )
