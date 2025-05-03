from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog, QHBoxLayout
from PyQt6.QtCore import Qt
import subprocess
import os
import sys

from drive_manager import MOUNT_POINT


class PasswordWindow(QWidget):
    def __init__(self, device_name, previous_window, mount_point=MOUNT_POINT):
        super().__init__()
        self.device_name = device_name
        self.previous_window = previous_window
        if self.device_name.startswith("sd") and self.device_name[-1].isdigit():
            base_name = self.device_name[:-1]  # Extract base (e.g., "sda")
            last_num = int(self.device_name[-1]) + 1  # Increment last digit
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

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Label
        self.label = QLabel(f"Password for {device_name}:")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E0E0E0;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Password input field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            padding: 6px; 
            font-size: 13px; 
            background-color: #424242; 
            border-radius: 4px; 
            color: white;
        """)
        layout.addWidget(self.password_input)

        # Horizontal Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Button style
        button_style = """
            QPushButton {
                background-color: #2D9B72;
                color: white;
                padding: 6px;
                border-radius: 4px;
                font-size: 13px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #32b97d;
            }
            QPushButton:pressed {
                background-color: #248f62;
            }
        """

        # Submit button
        self.submit_button = QPushButton("Unlock")
        self.submit_button.setStyleSheet(button_style)
        self.submit_button.clicked.connect(self.check_password)
        button_layout.addWidget(self.submit_button)

        # Change Password button
        self.change_password_button = QPushButton("Change")
        self.change_password_button.setStyleSheet(button_style)
        self.change_password_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.change_password_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def unlock_drive(self, password, sudo_password):
        """Unlock the LUKS-encrypted partition."""
        CRYPT_NAME = "encrypted_partition"

        if not self.device_name.startswith("/dev/"):
            self.device_name = f"/dev/{self.device_name}"

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
            if "already exists" in str(e):
                print("Drive is already unlocked.")
            else:
                print(f"Failed to unlock drive: {e}")
            return False

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def pre_checks(self, sudo_password):
        """Run pre-checks to ensure the partition is not already mounted and unlocked."""
        CRYPT_NAME = "encrypted_partition"
        try:
            if os.path.ismount(self.mount_point):
                process = subprocess.Popen(
                    ["sudo", "-S", "umount", self.mount_point],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=f"{sudo_password}\n")

                if process.returncode != 0:
                    print(f"Failed to unmount the partition: {stderr}")
                    return False

            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, text=True, input=f"{sudo_password}\n"
            )

            if "is active" in luks_status.stdout:
                process = subprocess.Popen(
                    ["sudo", "-S", "cryptsetup", "luksClose", CRYPT_NAME],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=f"{sudo_password}\n")

                if process.returncode != 0:
                    print(f"Failed to close the LUKS partition: {stderr}")
                    return False

            return True

        except subprocess.CalledProcessError as e:
            print(f"Pre-checks failed: {e}")
            return False

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

    def open_drive_window(self):
        from gui.drive_window import DriveWindow
        self.drive_window = DriveWindow(self.mount_point, self.previous_window)
        self.drive_window.show()
        self.close()

    def change_password(self):
        current_password, ok = QInputDialog.getText(self, 'Current Password',
                                                  'Enter current password:',
                                                  QLineEdit.EchoMode.Password)
        if not ok or not current_password:
            QMessageBox.critical(self, "Error", "Current password required")
            return

        new_password, ok = QInputDialog.getText(self, 'New Password', 'Enter new password:',
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

        sudo_password, ok = QInputDialog.getText(self, 'Sudo Password', 'Enter sudo password:',
                                              QLineEdit.EchoMode.Password)
        if not ok or not sudo_password:
            QMessageBox.critical(self, "Error", "Sudo password required")
            return

        try:
            if not self.pre_checks(sudo_password):
                QMessageBox.critical(self, "Error", "Pre-checks failed")
                return

            cmd_sudo = ["sudo", "-S", "echo", "sudo auth"]
            process_sudo = subprocess.Popen(cmd_sudo, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            process_sudo.communicate(input=f"{sudo_password}\n".encode())

            if process_sudo.returncode != 0:
                QMessageBox.critical(self, "Error", "Sudo authentication failed")
                return

            cmd_change_key = ["sudo", "cryptsetup", "luksChangeKey", self.device_name]
            process_change_key = subprocess.Popen(cmd_change_key, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            process_change_key.communicate(input=f"{current_password}\n{new_password}\n".encode())

            if process_change_key.returncode == 0:
                QMessageBox.information(self, "Success", "Password changed")
            else:
                QMessageBox.critical(self, "Error", "Failed to change password")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Password change failed: {e}")