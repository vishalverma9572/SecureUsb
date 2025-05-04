from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QInputDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt
import subprocess
import os

from drive_manager import MOUNT_POINT
from gui.drive_window import DriveWindow  # Ensure correct relative path


class PasswordWindow(QWidget):
    def __init__(self, device_name, previous_window, mount_point=MOUNT_POINT):
        super().__init__()
        self.device_name = device_name
        self.previous_window = previous_window

        if self.device_name.startswith("sd") and self.device_name[-1].isdigit():
            base_name = self.device_name[:-1]
            last_num = int(self.device_name[-1]) + 1
            self.device_name = f"/dev/{base_name}{last_num}"
        else:
            self.device_name = f"/dev/{self.device_name}"

        self.mount_point = "/mnt/private_partition"
        self.setWindowTitle("Drive Password")
        self.setGeometry(150, 150, 300, 150)
        self.setStyleSheet("""
            background-color: #212121;
            color: #E0E0E0;
            font-family: 'Segoe UI';
        """)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        self.init_password_ui()
        self.setLayout(self._layout)

    def init_password_ui(self):
        # Title Label
        self.label = QLabel(f"Password for {self.device_name}:")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E0E0E0;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.label)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            padding: 6px;
            font-size: 13px;
            background-color: #424242;
            border-radius: 4px;
            color: white;
        """)
        self._layout.addWidget(self.password_input)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        button_style = """
            QPushButton{
                background-color: #65a465;  /* Greenish shade similar to Pop!_OS */
                 min-width: 100px;
                 padding: 6px;
                border-radius: 4px;
                font-size: 13px;
                color: white;
            }
            QPushButton:hover {
                background-color: #76b476;  /* Light green when hovered */
            }
            QPushButton:pressed {
                background-color: #6b9d6b;  /* Darker green when pressed */
            }
        """

        # Unlock button
        self.submit_button = QPushButton("Unlock")
        self.submit_button.setStyleSheet(button_style)
        self.submit_button.clicked.connect(self.check_password)
        button_layout.addWidget(self.submit_button)

        # Change Password button
        self.change_password_button = QPushButton("Change")
        self.change_password_button.setStyleSheet(button_style)
        self.change_password_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.change_password_button)

        self._layout.addLayout(button_layout)

    def check_password(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.critical(self, "Error", "Password cannot be empty!")
            return

        sudo_password, ok = QInputDialog.getText(self, 'Sudo Password', 'Enter sudo password:',
                                                 QLineEdit.EchoMode.Password)
        if ok and sudo_password:
            if self.unlock_drive(password, sudo_password):
                self.open_drive_window()
            else:
                QMessageBox.critical(self, "Error", "Failed to unlock drive!")
        else:
            QMessageBox.critical(self, "Error", "Sudo password required")

    def unlock_drive(self, password, sudo_password):
        CRYPT_NAME = "encrypted_partition"
        try:
            self.pre_checks(sudo_password)

            subprocess.run(
                ["sudo", "cryptsetup", "luksOpen", self.device_name, CRYPT_NAME],
                input=password.encode(),
                check=True
            )

            if not os.path.exists(self.mount_point):
                os.makedirs(self.mount_point)

            subprocess.run(
                ["sudo", "mount", f"/dev/mapper/{CRYPT_NAME}", self.mount_point],
                input=sudo_password.encode(),
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to unlock drive: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def pre_checks(self, sudo_password):
        CRYPT_NAME = "encrypted_partition"
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(
                    ["sudo", "-S", "umount", self.mount_point],
                    input=f"{sudo_password}\n", text=True, check=True
                )

            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, text=True, input=f"{sudo_password}\n"
            )

            if "is active" in luks_status.stdout:
                subprocess.run(
                    ["sudo", "-S", "cryptsetup", "luksClose", CRYPT_NAME],
                    input=f"{sudo_password}\n", text=True, check=True
                )

            return True
        except subprocess.CalledProcessError as e:
            print(f"Pre-checks failed: {e}")
            return False
    def open_drive_window(self):
        # Hide the password-related widgets
        self.label.setVisible(False)
        self.password_input.setVisible(False)
        self.submit_button.setVisible(False)
        self.change_password_button.setVisible(False)

        # Clear old widgets
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
             child.widget().setParent(None)

        # Load DriveWindow inside the current window (self)
        self.drive_window = DriveWindow(self.mount_point, self.previous_window)
        self._layout.addWidget(self.drive_window)

     # Refresh layout to ensure proper rendering
        self.setLayout(self._layout)

    def change_password(self):
        current_password, ok = QInputDialog.getText(self, 'Current Password',
                                                    'Enter current password:',
                                                    QLineEdit.EchoMode.Password)
        if not ok or not current_password:
            QMessageBox.critical(self, "Error", "Current password required")
            return

        new_password, ok = QInputDialog.getText(self, 'New Password',
                                                'Enter new password:',
                                                QLineEdit.EchoMode.Password)
        if not ok or not new_password:
            QMessageBox.critical(self, "Error", "New password required")
            return

        confirm_password, ok = QInputDialog.getText(self, 'Confirm Password',
                                                    'Confirm new password:',
                                                    QLineEdit.EchoMode.Password)
        if not ok or new_password != confirm_password:
            QMessageBox.critical(self, "Error", "Passwords don't match")
            return

        sudo_password, ok = QInputDialog.getText(self, 'Sudo Password',
                                                 'Enter sudo password:',
                                                 QLineEdit.EchoMode.Password)
        if not ok or not sudo_password:
            QMessageBox.critical(self, "Error", "Sudo password required")
            return

        try:
            if not self.pre_checks(sudo_password):
                QMessageBox.critical(self, "Error", "Pre-checks failed")
                return

            process_sudo = subprocess.run(
                ["sudo", "-S", "echo", "auth"],
                input=f"{sudo_password}\n", text=True
            )

            if process_sudo.returncode != 0:
                QMessageBox.critical(self, "Error", "Sudo authentication failed")
                return

            process_change_key = subprocess.run(
                ["sudo", "cryptsetup", "luksChangeKey", self.device_name],
                input=f"{current_password}\n{new_password}\n".encode(),
                text=True
            )

            if process_change_key.returncode == 0:
                QMessageBox.information(self, "Success", "Password changed")
            else:
                QMessageBox.critical(self, "Error", "Failed to change password")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Password change failed: {e}")
