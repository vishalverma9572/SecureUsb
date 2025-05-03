from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class USBCard(QFrame):
    def __init__(self, device_name, mount_point, base_dir, on_select):
        super().__init__()

        # Set professional dark style matching the Pop!_OS color scheme
        self.setStyleSheet("""
            QFrame {
                background-color: #2e2e2e;  /* Dark background for card */
                border: 1px solid #444;     /* Lighter border for subtle separation */
                border-radius: 12px;        /* Rounded corners */
                padding: 15px;              /* Padding for spacing */
            }

            QLabel {
                color: #d0d0d0;             /* Light grey text */
                font-size: 14px;
            }

            QPushButton {
                background-color: #3b8c3a;  /* Green button background */
                color: white;                /* White text */
                padding: 8px 16px;           /* Padding for button */
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover {
                background-color: #4caf50;  /* Lighter green on hover */
            }

            QPushButton:pressed {
                background-color: #388e3c;  /* Darker green when pressed */
            }

            QLabel#deviceName {
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#mountPoint {
                color: #aaa;                /* Grey color for mount point */
                font-size: 12px;
            }
        """)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Layout
        layout = QVBoxLayout()

        # Device icon
        icon_label = QLabel()
        icon_path = os.path.join(base_dir, "..", "resources", "usb_generic.jpg")
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Device name and mount point
        label = QLabel(f"<span id='deviceName'>{device_name}</span><br><span id='mountPoint'>Mount Point: {mount_point}</span>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Select button
        open_button = QPushButton("Select")
        open_button.clicked.connect(lambda: on_select(device_name, mount_point))
        layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set layout for the card
        self.setLayout(layout)
