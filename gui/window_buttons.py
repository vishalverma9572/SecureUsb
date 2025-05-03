from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QWidget
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize
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

        # Logo (leftmost)
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # USB icon and title in a tight sub-layout
        icon_title_layout = QHBoxLayout()
        icon_title_layout.setSpacing(5)  # Reduce spacing here
        icon_title_layout.setContentsMargins(0, 0, 0, 0)

        self.usb_icon_label = QLabel()
        usb_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "usb.png")
        usb_pixmap = QPixmap(usb_icon_path)
        if not usb_pixmap.isNull():
            self.usb_icon_label.setPixmap(
                usb_pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        self.usb_icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel("SecureUsb")
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        icon_title_layout.addWidget(self.usb_icon_label)
        icon_title_layout.addWidget(self.title_label)

        icon_title_widget = QWidget()
        icon_title_widget.setLayout(icon_title_layout)

        # Load custom icons
        base_dir = os.path.dirname(os.path.abspath(__file__))
        min_icon_path = os.path.join(base_dir, "icons/min.png")
        max_icon_path = os.path.join(base_dir, "icons/max.png")
        close_icon_path = os.path.join(base_dir, "icons/close.png")

        # Minimize button
        self.min_button = QPushButton()
        self.min_button.setIcon(QIcon(QPixmap(min_icon_path)))
        self.min_button.setIconSize(QSize(24, 24))
        self._style_button(self.min_button)

        # Maximize button
        self.max_button = QPushButton()
        self.max_button.setIcon(QIcon(QPixmap(max_icon_path)))
        self.max_button.setIconSize(QSize(24, 24))
        self._style_button(self.max_button)

        # Close button
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(QPixmap(close_icon_path)))
        self.close_button.setIconSize(QSize(24, 24))
        self._style_button(self.close_button)

        # Connect actions
        self.min_button.clicked.connect(self.minimize_window)
        self.max_button.clicked.connect(self.maximize_window)
        self.close_button.clicked.connect(self.close_window)

        # Tooltips
        self.min_button.setToolTip("Minimize")
        self.max_button.setToolTip("Maximize")
        self.close_button.setToolTip("Close")

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.min_button)
        button_layout.addWidget(self.max_button)
        button_layout.addWidget(self.close_button)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add widgets to branding layout
        branding_layout.addWidget(self.logo_label)
        branding_layout.addWidget(icon_title_widget)
        branding_layout.addStretch()
        branding_layout.addLayout(button_layout)

        # Separator line
        self.line = QWidget(self)
        self.line.setFixedHeight(2)
        self.line.setStyleSheet("background-color: #666666;")

        # Final layout
        header_layout = QVBoxLayout()
        header_layout.addLayout(branding_layout)
        header_layout.addWidget(self.line)

        self.setLayout(header_layout)

    def _style_button(self, button):
        button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
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
