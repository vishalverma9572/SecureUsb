import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QProgressBar
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt

class USBCard(QFrame):
    def __init__(self, device_name, mount_point, base_dir, on_select):
        super().__init__()
        self.device_name = device_name
        self.mount_point = mount_point
        self.on_select = on_select

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Styling without hover effect
        self.setStyleSheet("""
            QFrame {
                background-color: #2e2e2e;
                padding: 15px;
                border-radius: 12px;
            }
            QLabel {
                color: #d0d0d0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3b8c3a;  /* Original greenish color */
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4caf50;  /* Slightly lighter green on hover */
            }
            QPushButton:pressed {
                background-color: #388e3c;  /* Darker green on press */
            }
            QPushButton#toggleButton {
                background-color: #65a465;  /* Greenish shade similar to Pop!_OS */
                border-radius: 6px;
            }
            QPushButton#toggleButton:hover {
                background-color: #76b476;  /* Light green when hovered */
            }
            QPushButton#toggleButton:pressed {
                background-color: #6b9d6b;  /* Darker green when pressed */
            }
            QLabel#deviceName {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#mountPoint {
                color: #aaa;
                font-size: 12px;
            }
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #1e1e1e;
                height: 10px;  # Shorter height for the progress bar
                min-width: 120px;  # Reduced width here too
                text-align: right;
                padding-right: 6px;
                font-size: 11px;
                color: #cccccc;
            }
            QProgressBar::chunk {
                background-color: #3b8c3a;
                border-radius: 6px;
            }
        """)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Device icon
        icon_label = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "drive.png")
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Device name
        name_label = QLabel(device_name)
        name_label.setObjectName("deviceName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(name_label)

        # Mount point
        self.mount_point_label = QLabel(f"Mount Point: {mount_point}")
        self.mount_point_label.setObjectName("mountPoint")
        self.mount_point_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mount_point_label.setVisible(False)
        text_layout.addWidget(self.mount_point_label)

        # Progress bar and storage info
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setMinimumWidth(120)  # Reduced width here too
        text_layout.addSpacing(6)
        text_layout.addWidget(self.progress_bar)

        self.update_storage_bar()

        # Add the text layout to the main layout
        main_layout.addLayout(text_layout)

        # Toggle button
        self.toggle_button = QPushButton("Show Mount Point")
        self.toggle_button.setObjectName("toggleButton")
        self.toggle_button.clicked.connect(self.toggle_mount_point)
        main_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(main_layout)

    def update_storage_bar(self):
        try:
            # Check if mount point exists and is valid
            if not os.path.ismount(self.mount_point):
                self.progress_bar.setFormat("Mount point is not valid")
                self.progress_bar.setValue(0)
                return

            # Check read access to the mount point
            if not os.access(self.mount_point, os.R_OK):
                self.progress_bar.setFormat("Permission denied")
                self.progress_bar.setValue(0)
                return

            print(f"Checking stats for mount point: {self.mount_point}")
            stats = os.statvfs(self.mount_point)

            total_bytes = stats.f_frsize * stats.f_blocks
            free_bytes = stats.f_frsize * stats.f_bavail
            used_bytes = total_bytes - free_bytes

            total_gb = total_bytes / (1024 ** 3)
            free_gb = free_bytes / (1024 ** 3)
            used_percent = int((used_bytes / total_bytes) * 100) if total_bytes else 0

            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(used_percent)
            self.progress_bar.setFormat(f"{free_gb:.1f} GB free of {total_gb:.1f} GB")

        except Exception as e:
            print(f"Error: {e}")
            self.progress_bar.setFormat("Storage info unavailable")
            self.progress_bar.setValue(0)

    def toggle_mount_point(self):
        is_visible = self.mount_point_label.isVisible()
        self.mount_point_label.setVisible(not is_visible)
        self.toggle_button.setText("Hide Mount Point" if not is_visible else "Show Mount Point")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_select(self.device_name, self.mount_point)
