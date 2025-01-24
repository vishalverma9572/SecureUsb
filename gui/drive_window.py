import os
import subprocess
import shutil
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QInputDialog, QLineEdit
from PyQt6.QtGui import QIcon
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

        # Back button with icon at the top left corner
        top_layout = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("resources/back_icon.png"))  # Set the icon
        self.back_button.setStyleSheet("""
            QPushButton { background-color: #A9A9A9; color: white; padding: 5px; border-radius: 5px; }
            QPushButton:hover { background-color: #8b8b8b; }
        """)
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

        # Add File button
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.add_file_button.clicked.connect(self.add_file)
        layout.addWidget(self.add_file_button, alignment=Qt.AlignmentFlag.AlignLeft)

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

    def add_file(self):
        """Allow the user to select a file, encrypt it, and save it to the drive."""
        try:
            if not os.path.ismount(self.mount_point):
                QMessageBox.warning(self, "Warning", "Partition is not mounted.")
                return

            file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Encrypt and Move")
            if file_path:
                password, ok = QInputDialog.getText(self, "Encryption Password", "Enter the encryption password for this file:", QLineEdit.EchoMode.Password)
                if not ok or not password:
                    return

                confirm_password, ok = QInputDialog.getText(self, "Encryption Password", "Re-enter the encryption password:", QLineEdit.EchoMode.Password)
                if not ok or password != confirm_password:
                    QMessageBox.critical(self, "Error", "Passwords do not match.")
                    return

                sudo_password, ok = QInputDialog.getText(self, "Sudo Password", "Enter your sudo password:", QLineEdit.EchoMode.Password)
                if not ok or not sudo_password:
                    return

                destination = os.path.join(self.mount_point, "." + os.path.basename(file_path) + ".enc")
                encrypted_file = self.encrypt_file(file_path, password)
                # Use 'sudo' to move the file with provided sudo password
                subprocess.run(["sudo", "-S", "mv", encrypted_file, destination], input=f"{sudo_password}\n", text=True, check=True)
                QMessageBox.information(self, "Success", f"File '{os.path.basename(file_path)}' encrypted and moved.")
                self.load_files()
        except Exception as e:
            logging.error(f"Failed to move and encrypt file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to move and encrypt file: {e}")

    def encrypt_file(self, file_path, password):
        """Encrypt a file using AES."""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        import os

        key = self.derive_key(password)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(file_path, 'rb') as f:
            data = f.read()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_file_path = file_path + ".enc"

        with open(encrypted_file_path, 'wb') as f:
            f.write(iv + encrypted_data)

        return encrypted_file_path

    def derive_key(self, password):
        """Derive a key from the given password."""
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'salt_',  # This should be a securely generated salt
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
