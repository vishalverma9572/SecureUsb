from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout,
    QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import os

from usb_manager import list_usb_devices, check_public_partition
from gui.password_window import PasswordWindow
from .window_buttons import BrandingHeader
from .usb_card import USBCard


class USBDeviceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecureUsb - USB Device List")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.show()
        self.showMaximized()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Set modern dark style matching Pop!_OS color scheme
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #d0d0d0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }

            QLabel#headingLabel {
                color: #a4d6a4;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 0;
            }

            QLabel {
                color: #bbbbbb;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QPushButton#usbButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                font-size: 18px;
                padding: 0;
            }

            QPushButton#usbButton:hover {
                color: #a4d6a4;
            }

            QPushButton#usbButton:pressed {
                color: #4c8c4a;
            }
        """)

        self.setup_ui()
        QTimer.singleShot(0, self.refresh_usb_list)

    def setup_ui(self):
        # Branding Header
        self.branding_header = BrandingHeader(self)

        # Heading Label
        self.heading_label = QLabel("Drives:")
        self.heading_label.setObjectName("headingLabel")
        self.heading_label.setFont(QFont("Segoe UI", 16))
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Refresh Button
        self.refresh_button = QPushButton("⟳")
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setToolTip("Refresh USB Devices")
        self.refresh_button.setObjectName("usbButton")
        self.refresh_button.clicked.connect(self.refresh_usb_list)

        # Back Button
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(100, 40)
        self.back_button.setToolTip("Back to USB Device List")
        self.back_button.setObjectName("usbButton")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setVisible(False)

        # Header layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.addWidget(self.heading_label)
        self.header_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.header_layout.addWidget(self.back_button)
        self.header_layout.addWidget(self.refresh_button)

        # Content layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(30, 2, 30, 30)
        self.content_layout.setSpacing(15)
        self.content_layout.addLayout(self.header_layout)

        # Scroll area and container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.usb_container = QWidget()
        self.usb_layout = QVBoxLayout(self.usb_container)
        self.usb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.usb_layout.setSpacing(12)

        self.scroll_area.setWidget(self.usb_container)
        self.content_layout.addWidget(self.scroll_area)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.branding_header)
        self.main_layout.addLayout(self.content_layout)

        self.setLayout(self.main_layout)

    def refresh_usb_list(self):
        # Clear any USB device cards
        for i in reversed(range(self.usb_layout.count())):
            widget = self.usb_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        devices = list_usb_devices()

        if devices:
            for device_name, mount_point in devices:
                if mount_point:
                    self.add_usb_card(device_name, mount_point)
        else:
            no_usb_label = QLabel("No USB devices detected.")
            no_usb_label.setStyleSheet("color: #777; font-style: italic; padding: 10px;")
            self.usb_layout.addWidget(no_usb_label)

    def add_usb_card(self, device_name, mount_point):
        card = USBCard(
            device_name=device_name,
            mount_point=mount_point,
            base_dir=self.base_dir,
            on_select=self.handle_usb_selection
        )
        self.usb_layout.addWidget(card)

    def handle_usb_selection(self, device_name, mount_point):
        if check_public_partition(mount_point):
            self.show_password_window(device_name, mount_point)
        else:
            QMessageBox.critical(self, "Invalid Device", "The selected drive is not a SecureUsb device.")

    def show_password_window(self, device_name, mount_point):
        # Hide all USB listing-related widgets
        self.scroll_area.setVisible(False)

        # Add password window
        self.password_window = PasswordWindow(device_name, self, mount_point)
        self.content_layout.addWidget(self.password_window)

        self.back_button.setVisible(True)
        self.refresh_button.setVisible(False)
        # self.heading_label.setText("Enter Password")

    def go_back(self):
        # Remove password window if exists
        if hasattr(self, "password_window"):
            self.content_layout.removeWidget(self.password_window)
            self.password_window.deleteLater()
            del self.password_window

        # Restore USB listing layout
        self.heading_label.setText("Drives:")
        self.scroll_area.setVisible(True)
        self.back_button.setVisible(False)
        self.refresh_button.setVisible(True)
        self.refresh_usb_list()
