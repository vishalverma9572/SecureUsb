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

        # Adjust device name to standard format
        if self.device_name.startswith("sd") and self.device_name[-1].isdigit():
            base_name = self.device_name[:-1]
            last_num = int(self.device_name[-1]) + 1
            self.device_name = f"/dev/{base_name}{last_num}"
        else:
            self.device_name = f"/dev/{self.device_name}"

        self.mount_point = "/mnt/private_partition"
        self.setWindowTitle("Secure Drive Access")
        self.setGeometry(150, 150, 350, 180)
        self.setStyleSheet("""
            QWidget {
                 /* Dark background */
                color: #F5F5F5; /* Light gray text */
                font-family: 'Ubuntu', 'Segoe UI', Tahoma, Geneva, sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #B0B0B0; /* Soft gray for labels */
                margin-bottom: 10px;
            }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                background-color: #272727; /* Darker gray input */
                border: 0.2px solid #FAFAFA;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border-color: 1px solid #8A9FFF; /* Soft blue for focus */
            }
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                color: white;
                border: none;
                margin-top: 15px;
                cursor: pointer;
            }
            QPushButton#unlockButton {
                background-color: #4caf50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton#unlockButton:hover {
                background-color: #4caf50;
            }
            QPushButton#unlockButton:pressed {
                background-color: #388e3c;
            }
            QPushButton#changePasswordButton {
                background-color: #4caf50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton#changePasswordButton:hover {
                background-color: #4caf50;
            }
            QPushButton#changePasswordButton:pressed {
                background-color: #388e3c;
            }
            QHBoxLayout {
                margin-top: 20px;
            }
        """)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(15)

        self.init_password_ui()
        self.setLayout(self._layout)

    def init_password_ui(self):
        # Title Label
        self.label = QLabel(f"Enter password for {self.device_name}:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.label)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._layout.addWidget(self.password_input)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Unlock button with specific object name
        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.setObjectName("unlockButton")
        self.unlock_button.clicked.connect(self.check_password)
        button_layout.addWidget(self.unlock_button)

        # Change Password button with a specific object name
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setObjectName("changePasswordButton")
        self.change_password_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.change_password_button)

        self._layout.addLayout(button_layout)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the content

    def check_password(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.critical(self, "Error", "Password cannot be empty!")
            return

        sudo_password, ok = QInputDialog.getText(self, 'Sudo Password', 'Enter your administrator (sudo) password:',
                                                 QLineEdit.EchoMode.Password)
        if ok and sudo_password:
            if self.unlock_drive(password, sudo_password):
                self.open_drive_window()
            else:
                QMessageBox.critical(self, "Error", "Failed to unlock drive. Incorrect password or insufficient permissions.")
        else:
            QMessageBox.critical(self, "Error", "Sudo password is required to unlock the drive.")

    def unlock_drive(self, password, sudo_password):
        CRYPT_NAME = "encrypted_partition"
        try:
            self.pre_checks(sudo_password)

            subprocess.run(
                ["sudo", "cryptsetup", "luksOpen", self.device_name, CRYPT_NAME],
                input=password.encode('utf-8') + b'\n',  # Add newline for password input
                check=True,
                stderr=subprocess.PIPE
            )

            if not os.path.exists(self.mount_point):
                os.makedirs(self.mount_point)

            subprocess.run(
                ["sudo", "mount", f"/dev/mapper/{CRYPT_NAME}", self.mount_point],
                input=sudo_password.encode('utf-8') + b'\n',  # Add newline for sudo password
                check=True,
                stderr=subprocess.PIPE
            )
            return True
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            print(f"Failed to unlock drive: {e} - {error_message}")
            QMessageBox.critical(self, "Error", f"Failed to unlock drive: {error_message}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return False

    def pre_checks(self, sudo_password):
        CRYPT_NAME = "encrypted_partition"
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(
                    ["sudo", "-S", "umount", self.mount_point],
                    input=sudo_password.encode('utf-8') + b'\n', check=True,
                    stderr=subprocess.PIPE
                )

            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, input=sudo_password.encode('utf-8') + b'\n'
            )
            luks_stdout = luks_status.stdout.decode('utf-8')

            if "is active" in luks_stdout:
                subprocess.run(
                    ["sudo", "-S", "cryptsetup", "luksClose", CRYPT_NAME],
                    input=sudo_password.encode('utf-8') + b'\n', check=True,
                    stderr=subprocess.PIPE
                )

            return True
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            print(f"Pre-checks failed: {e} - {error_message}")
            QMessageBox.critical(self, "Error", f"Pre-checks failed: {error_message}")
            return False

    def open_drive_window(self):
        # Hide the password-related widgets
        self.label.setVisible(False)
        self.password_input.setVisible(False)
        self.unlock_button.setVisible(False)
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
            QMessageBox.critical(self, "Error", "Current password is required.")
            return

        new_password, ok = QInputDialog.getText(self, 'New Password',
                                                'Enter new password:',
                                                QLineEdit.EchoMode.Password)
        if not ok or not new_password:
            QMessageBox.critical(self, "Error", "New password is required.")
            return

        confirm_password, ok = QInputDialog.getText(self, 'Confirm New Password',
                                                    'Confirm new password:',
                                                    QLineEdit.EchoMode.Password)
        if not ok or new_password != confirm_password:
            QMessageBox.critical(self, "Error", "New passwords do not match.")
            return

        sudo_password, ok = QInputDialog.getText(self, 'Sudo Password',
                                                 'Enter your administrator (sudo) password:',
                                                 QLineEdit.EchoMode.Password)
        if not ok or not sudo_password:
            QMessageBox.critical(self, "Error", "Sudo password is required to change the password.")
            return

        try:
            if not self.pre_checks(sudo_password):
                QMessageBox.critical(self, "Error", "Pre-checks failed.")
                return

            process_sudo = subprocess.run(
                ["sudo", "-S", "echo", "auth"],
                input=f"{sudo_password}\n".encode(), text=True,
                stderr=subprocess.PIPE
            )

            if process_sudo.returncode != 0:
                error_message = process_sudo.stderr.decode().strip()
                QMessageBox.critical(self, "Error", f"Sudo authentication failed: {error_message}")
                return

            process_change_key = subprocess.run(
                ["sudo", "cryptsetup", "luksChangeKey", self.device_name],
                input=f"{current_password}\n{new_password}\n{new_password}\n".encode(), # Need to provide new password twice
                text=True,
                stderr=subprocess.PIPE
            )

            if process_change_key.returncode == 0:
                QMessageBox.information(self, "Success", "Password for the encrypted drive has been successfully changed.")
            else:
                error_message = process_change_key.stderr.decode().strip()
                QMessageBox.critical(self, "Error", f"Failed to change password: {error_message}")

        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            QMessageBox.critical(self, "Error", f"Password change operation failed: {error_message}")
