import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class DriveWindow(QWidget):
    def __init__(self, mount_point, previous_window):
        super().__init__()

        self.mount_point = mount_point
        self.previous_window = previous_window  # Store reference to previous window

        self.setWindowTitle("Drive Contents")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet("background-color: #1e1e2e; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        # Back button at the top left corner
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Unmount and Go Back")
        self.back_button.setStyleSheet("background-color: #A9A9A9; color: white; padding: 5px; border-radius: 5px;")
        self.back_button.clicked.connect(self.unmount_and_go_back)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        self.label = QLabel(f"Files in {mount_point}:")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("background-color: #2e2e3e; color: white; font-size: 14px; padding: 5px;")
        layout.addWidget(self.file_list)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.refresh_button.clicked.connect(self.load_files)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        self.load_files()

    def load_files(self):
        self.file_list.clear()
        try:
            files = os.listdir(self.mount_point)
            self.file_list.addItems(files if files else ["No files found"])
        except Exception as e:
            self.file_list.addItem(f"Error: {e}")

    def unmount_and_go_back(self):
        """Forcefully unmount the partition and clean up before going back."""
        try:
            print(f"Attempting to force unmount the partition at {self.mount_point}...")
            subprocess.run(["sudo", "umount", "-f", self.mount_point], check=True)
            print("Partition unmounted successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to unmount the partition: {e}")
        self.previous_window.show()
        self.close()
