from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton
from src.core.shared import shared_data

class GscManagementTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        games = list(shared_data.keys())
        print( "Loading games list" )
        print( games )

        # Clickable list
        self.list_widget = QListWidget()
        self.list_widget.addItems( games )
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        # This is what creates the style of the list to select the game
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                font-size: 14px;
                min-height: {min(400, len(games) * 35)}px;
                max-height: {min(600, len(games) * 40)}px;
            }}
        """)

        layout.addWidget(self.list_widget)

        # Button to run function
        self.btn_run = QPushButton("Run Action")
        self.btn_run.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.btn_run)

        layout.addStretch()

    def on_item_clicked(self, item):
        print(f"Selected: {item.text()}")          # ← replace with your logic

    def on_run_clicked(self):
        current = self.list_widget.currentItem()
        if current:
            print(f"Running action on: {current.text()}")
        else:
            print("No item selected")