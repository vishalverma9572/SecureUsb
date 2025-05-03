from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize
import os

from usb_manager import list_usb_devices, check_public_partition
from gui.password_window import PasswordWindow
from .window_buttons import WindowButtons  # Import WindowButtons component

class USBDeviceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecureUsb - USB Device List")
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #f0f0f0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLabel#headingLabel {
                color: #ffcc00;
                font-size: 20px;
                font-weight: bold;
            }
        """)

        # Set the frameless window hint
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # Show the window, then maximize
        self.show()
        self.showMaximized()

        # Base directory for relative image loading
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Create the top panel with window buttons
        window_buttons = WindowButtons(self)

        main_layout = QVBoxLayout()
        top_layout = QVBoxLayout()
        top_layout.addWidget(window_buttons)

        # ========== Branding Panel ==========
        branding_layout = QVBoxLayout()
        content_layout = QVBoxLayout()

        # Branding Panel Content
        self.logo_label = QLabel()
        logo_path = os.path.join(self.base_dir, "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        branding_layout.addWidget(self.logo_label)

        self.title_label = QLabel("SecureUsb")
        self.title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        branding_layout.addWidget(self.title_label)

        branding_layout.addStretch()
        branding_layout.setContentsMargins(30, 30, 20, 30)

        # Content Panel Content
        self.heading_label = QLabel("Select your SecureUsb device to proceed 🔒")
        self.heading_label.setObjectName("headingLabel")
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.heading_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")

        self.usb_container = QWidget()
        self.usb_layout = QVBoxLayout(self.usb_container)
        self.usb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.usb_container)
        content_layout.addWidget(self.scroll_area)

        self.refresh_button = QPushButton(" Refresh USB Devices")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        refresh_icon = QIcon.fromTheme("view-refresh")
        self.refresh_button.setIcon(refresh_icon)
        self.refresh_button.setIconSize(QSize(24, 24))
        self.refresh_button.clicked.connect(self.refresh_usb_list)
        content_layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignCenter)

        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 30, 40, 30)

        # Combine panels
        top_layout.addLayout(branding_layout)
        top_layout.addLayout(content_layout)

        main_layout.addLayout(top_layout)

        self.setLayout(main_layout)

        # Populate USB list
        self.refresh_usb_list()

    def refresh_usb_list(self):
        devices = list_usb_devices()

        for i in reversed(range(self.usb_layout.count())):
            widget = self.usb_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if devices:
            for device_name, mount_point in devices:
                if mount_point:
                    self.add_usb_card(device_name, mount_point)
        else:
            no_usb_label = QLabel("No USB devices found")
            no_usb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.usb_layout.addWidget(no_usb_label)

    def add_usb_card(self, device_name, mount_point):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        card_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_path = os.path.join(self.base_dir, "..", "resources", "usb_generic.jpg")
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        label = QLabel(f"<b>{device_name}</b><br><span style='color: #aaa;'>Mount Point:</span> {mount_point}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("padding: 8px; font-size: 15px;")
        card_layout.addWidget(label)

        open_button = QPushButton("Select")
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        open_button.clicked.connect(lambda: self.handle_usb_selection(device_name, mount_point))
        card_layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        card.setLayout(card_layout)
        self.usb_layout.addWidget(card)

    def handle_usb_selection(self, device_name, mount_point):
        if check_public_partition(mount_point):
            self.open_password_window(device_name, mount_point)
        else:
            QMessageBox.critical(self, "Error", "SecureUsb not found! This is not a valid drive.")

    def open_password_window(self, device_name, mount_point):
        self.password_window = PasswordWindow(device_name, self, mount_point)
        self.password_window.show()
        self.close()