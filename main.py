"""拼豆图生成器的程序入口。"""

import ctypes
import os
import sys

# Anaconda 自带的 ICU DLL 会遮蔽 Windows 系统版本，而新版 Qt 需要后者。
# 在导入 PySide6 前预加载系统 DLL，避免 QtCore/QtWidgets 加载失败。
if sys.platform == "win32" and "Anaconda" in sys.version:
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    ctypes.WinDLL(os.path.join(system_root, "System32", "icuuc.dll"))

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
