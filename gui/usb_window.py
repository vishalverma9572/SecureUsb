from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout,
    QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont
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
                background-color: #2e2e2e;  /* Dark grey background */
                color: #d0d0d0;  /* Light grey text color */
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }

            QLabel#headingLabel {
                color: #a4d6a4;  /* Soft greenish color for the heading */
                font-size: 18px;
                font-weight: bold;
                padding: 12px 0;
            }

            QLabel {
                color: #bbbbbb;  /* Slightly darker grey for regular text */
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QPushButton#usbButton {
                background-color: transparent;
                color: #d0d0d0;  /* Light grey text */
                border: none;
                font-size: 18px;
                padding: 0;
            }

            QPushButton#usbButton:hover {
                color: #a4d6a4;  /* Light green on hover */
            }

            QPushButton#usbButton:pressed {
                color: #4c8c4a;  /* Darker green when pressed */
            }

            QLabel#headingLabel {
                color: #a4d6a4;  /* Soft greenish color for the heading */
            }
        """)

        # Branding Header
        self.branding_header = BrandingHeader(self)

        # Heading with Refresh Button
        self.heading_label = QLabel("Drives:")
        self.heading_label.setObjectName("headingLabel")
        self.heading_label.setFont(QFont("Segoe UI", 16))
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.refresh_button = QPushButton("⟳")
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setToolTip("Refresh USB Devices")
        self.refresh_button.setObjectName("usbButton")
        self.refresh_button.clicked.connect(self.refresh_usb_list)

        heading_layout = QHBoxLayout()
        heading_layout.setContentsMargins(0, 0, 0, 0)
        heading_layout.addWidget(self.heading_label)
        heading_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        heading_layout.addWidget(self.refresh_button)

        # Content Section
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 2, 30, 30)  # Reduced top margin from 10 to 5
        content_layout.setSpacing(15)
        content_layout.addLayout(heading_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.usb_container = QWidget()
        self.usb_layout = QVBoxLayout(self.usb_container)
        self.usb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.usb_layout.setSpacing(12)

        self.scroll_area.setWidget(self.usb_container)
        content_layout.addWidget(self.scroll_area)

        # Combine all layouts
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.branding_header)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        QTimer.singleShot(0, self.refresh_usb_list)

    def refresh_usb_list(self):
        devices = list_usb_devices()

        # Remove any previous device cards
        for i in reversed(range(self.usb_layout.count())):
            widget = self.usb_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

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
            self.open_password_window(device_name, mount_point)
        else:
            QMessageBox.critical(self, "Invalid Device", "The selected drive is not a SecureUsb device.")

    def open_password_window(self, device_name, mount_point):
        self.password_window = PasswordWindow(device_name, self, mount_point)
        self.password_window.show()
        self.close()
