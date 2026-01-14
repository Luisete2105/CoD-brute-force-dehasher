from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.core.shared_data import GameData
from src.core.hash_functions import black_ops_3_scr
from src.core.shared import shared_data
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

    shared_data = {}
    load_data_bo3(shared_data)

    window = MainWindow()
    window.shared_data = shared_data
    print(window.shared_data)
    window.setWindowTitle(APP_NAME)
    window.resize(1200, 800)
    window.show()

    return app.exec()


def load_data_bo3(shared_data: dict):
    game = "Black Ops 3"
    data = GameData()

    data.add_type("var",       black_ops_3_scr)
    data.add_type("hash",      black_ops_3_scr)
    data.add_type("namespace", black_ops_3_scr)
    data.add_type("class",     black_ops_3_scr)

    shared_data[game] = data

    print("Bo3 Loaded")