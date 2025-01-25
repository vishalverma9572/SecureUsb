import os
import subprocess
import shutil
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QFileDialog,
                             QMessageBox, QInputDialog, QLineEdit, QMenu)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import io
from PIL import Image



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
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.file_list)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.refresh_button.clicked.connect(self.load_files)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add File button
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.setStyleSheet(
            "background-color: #0078D7; color: white; padding: 10px; border-radius: 5px;")
        self.add_file_button.clicked.connect(self.add_file)
        layout.addWidget(self.add_file_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

        self.load_files()

    def show_context_menu(self, position):
        menu = QMenu()
        open_action = QAction("Open", self)
        download_action = QAction("Download", self)
        delete_action = QAction("Delete", self)  # Add delete option
        menu.addAction(open_action)
        menu.addAction(download_action)
        menu.addAction(delete_action)  # Add delete option to menu

        open_action.triggered.connect(self.open_selected_file)
        download_action.triggered.connect(self.download_selected_file)
        delete_action.triggered.connect(self.delete_selected_file)  # Connect to delete method

        menu.exec(self.file_list.viewport().mapToGlobal(position))

    def download_selected_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        file_name = selected_items[0].text()
        file_path = os.path.join(self.mount_point, file_name)

        # Warning message to the user
        warning_message = "Downloading files may be dangerous. We strongly recommend not to download."
        reply = QMessageBox.warning(self, "Warning", warning_message,
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Prompt for decryption password
            password, ok = QInputDialog.getText(self, "Decryption Password", "Enter the decryption password:",
                                                QLineEdit.EchoMode.Password)
            if not ok or not password:
                return

            # Prompt for sudo password
            sudo_password, ok = QInputDialog.getText(self, "Sudo Password", "Enter your sudo password:",
                                                     QLineEdit.EchoMode.Password)
            if not ok or not sudo_password:
                return

            try:
                decrypted_data = self.decrypt_file(file_path, password)

                # Create a new file name without the leading dot and .enc extension
                if file_name.startswith('.'):
                    file_name = file_name[1:]
                new_file_name = file_name.rsplit('.enc', 1)[0]

                # Create a temporary file with decrypted data
                temp_decrypted_file_path = os.path.join('/tmp', new_file_name)
                with open(temp_decrypted_file_path, 'wb') as temp_file:
                    temp_file.write(decrypted_data)

                # Ask for location to save the decrypted file
                save_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File", new_file_name)
                if save_path:
                    shutil.copy(temp_decrypted_file_path, save_path)
                    QMessageBox.information(self, "Success",
                                            f"File '{new_file_name}' decrypted and saved at {save_path}.")
                else:
                    QMessageBox.warning(self, "Error", "No save location chosen.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download and decrypt file: {e}")

    def delete_selected_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        file_name = selected_items[0].text()
        file_path = os.path.join(self.mount_point, file_name)

        reply = QMessageBox.warning(self, "Confirm Deletion", f"Are you sure you want to delete '{file_name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Prompt for sudo password
            sudo_password, ok = QInputDialog.getText(self, "Sudo Password", "Enter your sudo password:",
                                                     QLineEdit.EchoMode.Password)
            if not ok or not sudo_password:
                return

            try:
                # Use sudo to delete the file
                process = subprocess.run(
                    ['sudo', '-S', 'rm', '-f', file_path],
                    input=sudo_password + "\n",
                    text=True,
                    capture_output=True
                )

                if process.returncode == 0:
                    self.load_files()  # Refresh file list after deletion
                    QMessageBox.information(self, "Success", f"File '{file_name}' deleted successfully.")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete file: {process.stderr}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")


    def open_selected_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        file_name = selected_items[0].text()
        file_path = os.path.join(self.mount_point, file_name)

        password, ok = QInputDialog.getText(self, "Decryption Password", "Enter the decryption password:",
                                            QLineEdit.EchoMode.Password)
        if not ok or not password:
            return

        sudo_password, ok = QInputDialog.getText(self, "Sudo Password", "Enter your sudo password:",
                                                 QLineEdit.EchoMode.Password)
        if not ok or not sudo_password:
            return

        try:
            decrypted_data = self.decrypt_file(file_path, password)
            with Image.open(io.BytesIO(decrypted_data)) as img:
                img.show()
            QMessageBox.information(self, "Success", f"Decrypted file '{file_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

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
                password, ok = QInputDialog.getText(self, "Encryption Password",
                                                    "Enter the encryption password for this file:",
                                                    QLineEdit.EchoMode.Password)
                if not ok or not password:
                    return

                confirm_password, ok = QInputDialog.getText(self, "Encryption Password",
                                                            "Re-enter the encryption password:",
                                                            QLineEdit.EchoMode.Password)
                if not ok or password != confirm_password:
                    QMessageBox.critical(self, "Error", "Passwords do not match.")
                    return

                sudo_password, ok = QInputDialog.getText(self, "Sudo Password", "Enter your sudo password:",
                                                         QLineEdit.EchoMode.Password)
                if not ok or not sudo_password:
                    return

                destination = os.path.join(self.mount_point, "." + os.path.basename(file_path) + ".enc")
                encrypted_file = self.encrypt_file(file_path, password)
                # Use 'sudo' to move the file with provided sudo password
                subprocess.run(["sudo", "-S", "mv", encrypted_file, destination], input=f"{sudo_password}\n", text=True,
                               check=True)
                QMessageBox.information(self, "Success", f"File '{os.path.basename(file_path)}' encrypted and moved.")
                self.load_files()
        except Exception as e:
            logging.error(f"Failed to move and encrypt file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to move and encrypt file: {e}")

    def decrypt_file(self, file_path, password):
        """Decrypt a file using AES."""
        key = self.derive_key(password)  # Corrected reference to derive_key
        with open(file_path, 'rb') as f:
            iv = f.read(16)  # Read the IV (16 bytes)
            encrypted_data = f.read()  # The encrypted data

        # Use the same padding and decryption logic as during encryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Ensure proper unpadding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data

    def derive_key(self, password, salt=b'salt_', iterations=100000):
        """Derive a key from the given password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            print("unmounting device")
            self.unmount_drive()  # Unmount the drive before exiting
            event.accept()  # Close the window
        else:
            event.ignore()  # Cancel the close event

    def unmount_drive(self):
        try:
            subprocess.run(['sudo', 'umount', self.mount_point], check=True)
            QMessageBox.information(self, "Unmounted", "Drive successfully unmounted.")
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, "Error", "Failed to unmount the drive.")

