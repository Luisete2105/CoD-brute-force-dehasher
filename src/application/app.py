from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.core.config import APP_NAME, APP_STYLE


def run_application() -> int:
    app = QApplication([])

    # Optional: global style / palette
    app.setStyle("Fusion")              # or "Windows"
    app.setApplicationName(APP_NAME)

    if APP_STYLE:
        app.setStyleSheet(APP_STYLE)

    # Optional: high dpi support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.setWindowTitle(APP_NAME)
    window.resize(1200, 800)
    window.show()

    return app.exec()