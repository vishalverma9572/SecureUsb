from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from usb_manager import list_usb_devices, check_public_partition
from gui.password_window import PasswordWindow

class USBDeviceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecureUsb - USB Device List")
        self.setGeometry(100, 100, 500, 500)
        self.setStyleSheet("background-color: #1e1e2e; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        self.logo_label = QLabel()
        pixmap = QPixmap("gui/logo.png")
        self.logo_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        self.title_label = QLabel("SecureUsb")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.heading_label = QLabel("Select your SecureUsb pendrive to proceed 🔒")
        self.heading_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700; padding: 10px;")
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.heading_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.usb_container = QWidget()
        self.usb_layout = QVBoxLayout(self.usb_container)
        self.scroll_area.setWidget(self.usb_container)

        layout.addWidget(self.scroll_area)

        self.refresh_button = QPushButton("Refresh USB Devices")
        self.refresh_button.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.refresh_button.clicked.connect(self.refresh_usb_list)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        self.refresh_usb_list()

    def refresh_usb_list(self):
        devices = list_usb_devices()
        for i in reversed(range(self.usb_layout.count())):
            self.usb_layout.itemAt(i).widget().setParent(None)

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
            background-color: #2e2e3e;
            border-radius: 10px;
            margin: 10px auto;
            max-width: 350px;
            border: 1px solid #444;
        """)

        card_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/usb_generic.jpg")
        icon_label.setPixmap(icon_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        label = QLabel(f"{device_name} - Mount Point: {mount_point}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label)

        open_button = QPushButton("Select")
        open_button.setStyleSheet("background-color: #0078D7; color: white; padding: 5px; border-radius: 5px;")
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
        self.password_window = PasswordWindow(device_name, mount_point)
        self.password_window.show()
        self.close()
