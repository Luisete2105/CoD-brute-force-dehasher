# src/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout

# Import tabs lazily / on demand to help prevent circular imports
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._setup_tabs()

    def _setup_tabs(self):
        # Create tabs only when needed (lazy)
        from src.gsc.ui.tab_gsc import GscManagementTab
        from src.brute.ui.tab_brute import BruteForceTab
        from src.cfg.ui.tab_cfg import CfgManagementTab

        self.tabs.addTab(GscManagementTab(), "GSC Management")
        self.tabs.addTab(BruteForceTab(),    "Brute Force")
        self.tabs.addTab(CfgManagementTab(), "CFG Editor")