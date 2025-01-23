from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox, QFrame, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from usb_manager import list_usb_devices

class USBDeviceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecureUsb - USB Device List")
        self.setGeometry(100, 100, 500, 500)
        self.setStyleSheet("background-color: #1e1e2e; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        # Logo + Branding
        self.logo_label = QLabel()
        pixmap = QPixmap("gui/logo.png")  # Add your logo file in the `gui/` folder
        self.logo_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        self.title_label = QLabel("SecureUsb")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; text-align: center;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Catchy Heading
        self.heading_label = QLabel("Select your SecureUsb pendrive to proceed 🔒")
        self.heading_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700; text-align: center; padding: 10px;")
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.heading_label)

        # Scroll Area for USB devices
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.usb_container = QWidget()
        self.usb_layout = QVBoxLayout(self.usb_container)
        self.scroll_area.setWidget(self.usb_container)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        self.refresh_usb_list()

    def refresh_usb_list(self):
        devices = list_usb_devices()
        for i in reversed(range(self.usb_layout.count())):
            self.usb_layout.itemAt(i).widget().setParent(None)

        if devices:
            for device in devices:
                self.add_usb_card(device)
        else:
            no_usb_label = QLabel("No USB devices found")
            no_usb_label.setStyleSheet("font-size: 16px; padding: 10px;")
            no_usb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.usb_layout.addWidget(no_usb_label)

    def add_usb_card(self, device_name):
        """Creates a responsive card for each USB device."""
        card = QFrame()
        card.setStyleSheet("""
            background-color: #2e2e3e;
            border-radius: 10px;
            margin: 10px auto;
            max-width: 350px;
            border: 1px solid #444;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
        """)

        card_layout = QVBoxLayout()

        # USB Image
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/usb_generic.jpg")  # Add a generic USB image in the `resources/` folder
        icon_label.setPixmap(icon_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        # USB Name
        label = QLabel(device_name)
        label.setStyleSheet("font-size: 14px; text-align: center; padding-top: 5px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label)

        # Select Button
        open_button = QPushButton("Select")
        open_button.setStyleSheet("background-color: #0078D7; color: white; padding: 5px; border-radius: 5px;")
        open_button.clicked.connect(lambda: self.confirm_selection(device_name))
        card_layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        card.setLayout(card_layout)
        self.usb_layout.addWidget(card)

    def confirm_selection(self, device_name):
        """Shows a confirmation dialog when clicking a USB device."""
        msg = QMessageBox()
        msg.setWindowTitle("Confirm USB Selection")
        msg.setText(f"Are you sure this is the correct USB device?\n\n{device_name}")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)

        result = msg.exec()

        if result == QMessageBox.StandardButton.Yes:
            print(f"Opening USB: {device_name}")
            import subprocess
            subprocess.run(["xdg-open", f"/media/{device_name.split(' → ')[1]}"])

