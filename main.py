"""拼豆图生成器的程序入口。"""

import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

