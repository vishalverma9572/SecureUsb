import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
import sys


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
        self.heading_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #FFD700; text-align: center; padding: 10px;")
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

    def prompt_password(self):
        """Prompt the user to input the encryption password."""
        password = self.password_input.text().strip()
        if not password:
            QMessageBox.critical(self, "Error", "Password cannot be empty.")
            return None
        return password

    def unlock_partition(self, password):
        """Unlock the LUKS-encrypted partition."""
        # Automatically infer the encrypted partition name (e.g., sda1 -> sda2)
        encrypted_device_name = self.device_name[:-1] + str(int(self.device_name[-1]) + 1)

        try:
            subprocess.run(
                ["sudo", "cryptsetup", "luksOpen", encrypted_device_name, encrypted_device_name],
                input=password.encode(), check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e):
                QMessageBox.information(self, "Info", "Partition is already unlocked.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to unlock partition: {e}")
            return False

    def check_password(self):
        password = self.prompt_password()
        if password and self.unlock_partition(password):
            QMessageBox.information(self, "Success", f"{self.device_name} Unlocked!")
            self.close()  # Close this window after unlocking
        else:
            QMessageBox.critical(self, "Error", "Incorrect Password!")

    def go_back(self):
        """Switches back to the parent window."""
        self.parent_window.show()  # Show the parent window
        self.close()  # Close the current (Password) window
