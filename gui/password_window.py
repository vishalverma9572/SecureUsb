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
        self.previous_window = previous_window  # Store reference to previous window
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

        # Back button at the top left corner
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("background-color: #A9A9A9; color: white; padding: 5px; border-radius: 5px;")
        self.back_button.clicked.connect(self.go_back)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch()
        layout.addLayout(top_layout)

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

    def go_back(self):
        # Show the previous window and close the current one
        self.previous_window.show()
        self.close()

    def unlock_drive(self, password, sudo_password):
        """Unlock the LUKS-encrypted partition."""
        CRYPT_NAME = "encrypted_partition"  # Name for unlocked partition

        if not self.device_name.startswith("/dev/"):
            self.device_name = f"/dev/{self.device_name}"

        print(f"Using device: {self.device_name} with password: ")

        try:
            # Run pre-checks to ensure the partition is not already unlocked
            self.pre_checks(sudo_password)

            # Step 1: Unlock the LUKS partition
            print(f"Unlocking device: {self.device_name} with password: ")
            subprocess.run(
                ["sudo", "cryptsetup", "luksOpen", self.device_name, CRYPT_NAME],
                input=password.encode(),
                check=True
            )
            print("Drive unlocked successfully.")

            # Step 2: Mount the unlocked partition
            if not os.path.exists(self.mount_point):
                os.makedirs(self.mount_point)

            # Mount the partition
            subprocess.run(
                ["sudo", "mount", f"/dev/mapper/{CRYPT_NAME}", self.mount_point],
                input=sudo_password.encode(),  # Pass sudo password here
                check=True
            )

            print("Partition mounted successfully.")
            return True

        except subprocess.CalledProcessError as e:
            if "already exists" in str(e):
                print("Drive is already unlocked.")
            else:
                print(f"Failed to unlock drive: {e}")
                sys.exit(1)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

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
                stdout, stderr = process.communicate(input=f"{sudo_password}\n")

                if process.returncode == 0:
                    print("Unmounted the partition successfully.")
                else:
                    print(f"Failed to unmount the partition: {stderr}")
                    return False

            # Check if the LUKS partition is already open
            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, text=True, input=f"{sudo_password}\n"  # Pass sudo password here
            )

            if "is active" in luks_status.stdout:
                print(f"LUKS partition '{CRYPT_NAME}' is already active. Closing...")
                # Check if the partition is in use (to avoid closing it while in use)
                in_use_status = subprocess.run(
                    ["sudo", "lsof", "/dev/mapper/encrypted_partition"],
                    capture_output=True, text=True
                )

                if in_use_status.returncode == 0:
                    print(f"The partition is still in use by some process: {in_use_status.stdout}")
                    return False

                process = subprocess.Popen(
                    ["sudo", "-S", "cryptsetup", "luksClose", CRYPT_NAME],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=f"{sudo_password}\n")

                # Log output from luksClose to help debug
                print("luksClose Output:")
                print(stdout)
                print("luksClose Error:")
                print(stderr)

                if process.returncode == 0:
                    print("Closed the LUKS partition successfully.")
                else:
                    print(f"Failed to close the LUKS partition: {stderr}")
                    return False

            # Double-check if the LUKS partition is still active
            luks_status = subprocess.run(
                ["sudo", "-S", "cryptsetup", "status", CRYPT_NAME],
                capture_output=True, text=True, input=f"{sudo_password}\n"
            )

            if "is active" in luks_status.stdout:
                print(f"LUKS partition '{CRYPT_NAME}' is still active after closing.")
                return False

            return True

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
        self.drive_window = DriveWindow(self.mount_point, self.previous_window)  # Pass previous window reference
        self.drive_window.show()
        self.close()
