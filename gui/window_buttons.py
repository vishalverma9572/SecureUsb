from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore

class WindowButtons(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(30)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #f0f0f0;
                font-size: 18px;
                width: 30px;
                height: 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:focus {
                outline: none;
            }
        """)

        # Create minimize, maximize, and "B" buttons
        self.min_button = QPushButton("-")
        self.max_button = QPushButton("□")
        self.b_button = QPushButton("")  # Create the "B" button

        # Set icons (optional)
        self.min_button.setIcon(QIcon.fromTheme("window-minimize"))
        self.max_button.setIcon(QIcon.fromTheme("window-maximize"))
        self.b_button.setIcon(QIcon.fromTheme("window-close")) #use close icon.

        # Set the icon size
        icon_size = 18
        self.min_button.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.max_button.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.b_button.setIconSize(QtCore.QSize(icon_size, icon_size))

        # Connect buttons to actions
        self.min_button.clicked.connect(self.minimize_window)
        self.max_button.clicked.connect(self.maximize_window)
        self.b_button.clicked.connect(self.close_window)  # Connect "B" button

        # Layout for the buttons
        button_layout = QHBoxLayout(self)
        button_layout.setContentsMargins(0, 0, 10, 0)  # Margin from right
        button_layout.setSpacing(5)  # Space between buttons
        button_layout.addWidget(self.min_button)
        button_layout.addWidget(self.max_button)
        button_layout.addWidget(self.b_button)  # Add the "B" button

        # Align buttons to the right
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLayout(button_layout)

    def minimize_window(self):
        if self.parent():
            self.parent().showMinimized()

    def maximize_window(self):
        if self.parent():
            if self.parent().isMaximized():
                self.parent().showNormal()
            else:
                self.parent().showMaximized()

    def close_window(self):
        if self.parent():
            self.parent().close()
