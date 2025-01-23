from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class PasswordWindow(QWidget):
    def __init__(self, device_name, mount_point, parent_window):
        super().__init__()

        self.device_name = device_name
        self.mount_point = mount_point
        self.parent_window = parent_window  # Store reference to the parent window

        self.setWindowTitle("Unlock USB Drive")
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet("background-color: #1e1e2e; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        # Back Button
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("background-color: #333; color: white; padding: 5px; border-radius: 5px;")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Heading
        self.heading_label = QLabel(f"Enter password to unlock {device_name}")
        self.heading_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700; text-align: center; padding: 10px;")
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.heading_label)

        # Password Field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.setStyleSheet("padding: 10px; border-radius: 5px; background-color: #333; color: white;")
        layout.addWidget(self.password_input)

        # Unlock Button
        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.setStyleSheet("background-color: #0078D7; color: white; padding: 8px; border-radius: 5px;")
        self.unlock_button.clicked.connect(self.check_password)
        layout.addWidget(self.unlock_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def check_password(self):
        password = self.password_input.text()

        if password == "securepass":  # Replace with actual password checking logic
            QMessageBox.information(self, "Success", "USB Drive Unlocked!")
            self.close()  # Close this window after unlocking
        else:
            QMessageBox.critical(self, "Error", "Incorrect Password!")

    def go_back(self):
        """Switches back to the parent window (USBDeviceWindow)."""
        self.parent_window.show()  # Show the parent window
        self.close()  # Close the current (Password) window
