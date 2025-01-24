import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
import sys

from drive_manager import MOUNT_POINT

class PasswordWindow(QWidget):
    def __init__(self, device_name, mount_point=MOUNT_POINT):
        super().__init__()
        self.device_name = device_name
        if self.device_name.startswith("sd") and self.device_name[-1].isdigit():
            base_name = self.device_name[:-1]  # Extract base (e.g., "sda")
            last_num = int(self.device_name[-1]) + 1  # Increment last digit
            self.device_name = f"/dev/{base_name}{last_num}"
        else:
            self.device_name = f"/dev/{self.device_name}"
        self.mount_point = "/mnt/private_partition"
        self.setWindowTitle("Enter Password")
        self.setGeometry(150, 150, 400, 200)
        self.setStyleSheet("background-color: #2e2e3e; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        self.label = QLabel(f"Enter password for {device_name}:")
        self.label.setStyleSheet("font-size: 16px; padding: 5px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 5px; font-size: 14px;")
        layout.addWidget(self.password_input)

        self.submit_button = QPushButton("Unlock Drive")
        self.submit_button.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.submit_button.clicked.connect(self.check_password)
        layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def unlock_drive(self, password, sudo_password):
        CRYPT_NAME = "encrypted_partition"  # Name for unlocked partition

        if not self.device_name.startswith("/dev/"):
            self.device_name = f"/dev/{self.device_name}"

        print(f"Using device: {self.device_name}")
        print(f"Attempting to unlock with passphrase: {password}")  # Printing passphrase for debugging

        try:
            self.pre_checks(sudo_password)

            # Unlock the drive with the provided passphrase
            process = subprocess.Popen(
                ["sudo", "-S", "cryptsetup", "luksOpen", self.device_name, CRYPT_NAME],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Pass sudo password and passphrase
            stdin_input = f"{sudo_password}\n{password}\n"
            stdout, stderr = process.communicate(stdin_input)

            if process.returncode != 0:
                print(f"Failed to unlock drive: {stderr}")
                return False

            print(f"Drive unlocked successfully: {stdout}")

            if not os.path.exists(self.mount_point):
                os.makedirs(self.mount_point, exist_ok=True)

            # Mount the unlocked drive
            process = subprocess.run(
                ["sudo", "-S", "mount", f"/dev/mapper/{CRYPT_NAME}", self.mount_point],
                input=f"{sudo_password}\n",  # Pass sudo password here
                check=True,
                capture_output=True,
                text=True
            )

            print(f"Mount output: {process.stdout}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to unlock drive: {e}")
            return False

    def pre_checks(self, sudo_password):
        """Run pre-checks to ensure the partition is not already mounted and unlocked."""
        CRYPT_NAME = "encrypted_partition"
        try:
            # Check if the partition is already mounted, and unmount if necessary
            if os.path.ismount(self.mount_point):
                print(f"Partition is already mounted at {self.mount_point}. Unmounting...")
                process = subprocess.Popen(
                    ["sudo", "-S", "umount", self.mount_point],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Pass the sudo password for unmounting
                process.communicate(input=f"{sudo_password}\n")

                if process.returncode == 0:
                    print("Unmounted the partition successfully.")
                else:
                    print(f"Failed to unmount the partition: {process.stderr}")

            # Check if the LUKS partition is already open
            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, text=True, input=f"{sudo_password}\n"  # Pass sudo password here
            )

            if "is active" in luks_status.stdout:
                print(f"LUKS partition '{CRYPT_NAME}' is already active. Closing...")
                process = subprocess.Popen(
                    ["sudo", "-S", "cryptsetup", "luksClose", CRYPT_NAME],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Pass the sudo password to close the LUKS partition
                process.communicate(input=f"{sudo_password}\n")

                if process.returncode == 0:
                    print("Closed the LUKS partition successfully.")
                else:
                    print(f"Failed to close the LUKS partition: {process.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"Pre-checks failed: {e}")
            sys.exit(1)

    def check_password(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.critical(self, "Error", "Password cannot be empty!")
            return

        # Prompt for sudo password
        sudo_password, ok = QInputDialog.getText(self, 'Enter Sudo Password', 'Please enter your sudo password:',
                                                  QLineEdit.EchoMode.Password)
        if ok and sudo_password:
            if self.unlock_drive(password, sudo_password):
                self.open_drive_window()
            else:
                QMessageBox.critical(self, "Error", "Incorrect password! Try again.")
        else:
            QMessageBox.critical(self, "Error", "Sudo password is required.")

    def open_drive_window(self):
        from gui.drive_window import DriveWindow
        self.drive_window = DriveWindow(self.mount_point)
        self.drive_window.show()
        self.close()
