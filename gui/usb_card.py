# usb_card.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class USBCard(QFrame):
    def __init__(self, device_name, mount_point, base_dir, on_select):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout()

        icon_label = QLabel()
        icon_path = os.path.join(base_dir, "..", "resources", "usb_generic.jpg")
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        label = QLabel(f"<b>{device_name}</b><br><span style='color: #aaa;'>Mount Point:</span> {mount_point}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("padding: 8px; font-size: 15px;")
        layout.addWidget(label)

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
        open_button.clicked.connect(lambda: on_select(device_name, mount_point))
        layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
