"""图片与目标尺寸输入面板。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
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
    convert_requested = Signal(str, int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.image_path = ""
        self.path_label = QLabel("尚未选择图片")
        self.path_label.setWordWrap(True)

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

        convert_button = QPushButton("生成拼豆图")
        convert_button.clicked.connect(self._request_conversion)

        choose_layout = QHBoxLayout()
        choose_layout.addWidget(choose_button)
        choose_layout.addWidget(self.path_label, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(choose_layout)
        layout.addLayout(size_form)
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

    def _request_conversion(self) -> None:
        if self.image_path:
            self.convert_requested.emit(
                self.image_path,
                self.width_input.value(),
                self.height_input.value(),
            )

