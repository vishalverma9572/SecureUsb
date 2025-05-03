from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QWidget, QStyle
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import os


class BrandingHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the height of the branding header
        self.setFixedHeight(60)

        # Create the main layout for branding (logo, title, window buttons)
        branding_layout = QHBoxLayout()
        branding_layout.setContentsMargins(0, 0, 20, 0)
        branding_layout.setSpacing(20)

        # Logo
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Title
        self.title_label = QLabel("SecureUsb")
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Window buttons (minimize, maximize, close)
        self.min_button = QPushButton()
        self.min_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self._style_button(self.min_button)

        self.max_button = QPushButton()
        self.max_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self._style_button(self.max_button)

        self.close_button = QPushButton()
        self.close_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self._style_button(self.close_button)

        # Connect actions for window buttons
        self.min_button.clicked.connect(self.minimize_window)
        self.max_button.clicked.connect(self.maximize_window)
        self.close_button.clicked.connect(self.close_window)

        # Tooltips
        self.min_button.setToolTip("Minimize")
        self.max_button.setToolTip("Maximize")
        self.close_button.setToolTip("Close")

        # Window button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.min_button)
        button_layout.addWidget(self.max_button)
        button_layout.addWidget(self.close_button)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add elements to branding layout
        branding_layout.addWidget(self.logo_label)
        branding_layout.addWidget(self.title_label)
        branding_layout.addStretch()
        branding_layout.addLayout(button_layout)

        # Custom separator line
        self.line = QWidget(self)
        self.line.setFixedHeight(2)  # Slightly thicker separator
        self.line.setStyleSheet("background-color: #666666;")  # Grey line

        # Final header layout
        header_layout = QVBoxLayout()
        header_layout.addLayout(branding_layout)
        header_layout.addWidget(self.line)

        self.setLayout(header_layout)

    def _style_button(self, button):
        button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #d0d0d0;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #a4d6a4;  /* Light green on hover */
            }
            QPushButton:pressed {
                color: #4c8c4a;  /* Darker green when pressed */
            }
        """)

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
