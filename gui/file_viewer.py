import sys
import io
import subprocess
import os
import random
import time
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PIL import Image


class FileViewer(QWidget):
    def __init__(self, decrypted_data):
        super().__init__()
        self.decrypted_data = decrypted_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simultaneous File Viewer")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Opening file with all possible viewers...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        # Start all viewers in separate threads
        threading.Thread(target=self.open_as_text, daemon=True).start()
        threading.Thread(target=self.open_as_pdf, daemon=True).start()
        threading.Thread(target=self.open_as_image, daemon=True).start()
        threading.Thread(target=self.open_as_audio, daemon=True).start()
        threading.Thread(target=self.open_as_video, daemon=True).start()

        self.show()

    def overwrite_with_noise(self, file_path):
        try:
            with open(file_path, "wb") as f:
                f.write(os.urandom(1024 * 100))  # 100KB of random noise
        except Exception as e:
            print(f"[ERROR] Overwriting failed: {e}")

    def safe_open(self, extension, viewer_func):
        try:
            temp_file = f"tempfile_{extension}.{extension}"
            with open(temp_file, "wb") as f:
                f.write(self.decrypted_data)

            viewer_func(temp_file)

            time.sleep(10)
            self.overwrite_with_noise(temp_file)
            time.sleep(1)
            os.remove(temp_file)

        except Exception as e:
            print(f"[ERROR] Opening {extension} failed: {e}")

    def open_as_text(self):
        try:
            text = self.decrypted_data.decode("utf-8")
            temp_file = "tempfile.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(text)

            subprocess.Popen(["xdg-open", temp_file])

            time.sleep(10)
            self.overwrite_with_noise(temp_file)
            time.sleep(1)
            os.remove(temp_file)
        except Exception:
            pass

    def open_as_pdf(self):
        self.safe_open("pdf", lambda f: subprocess.Popen(["xdg-open", f]))

    def open_as_audio(self):
        self.safe_open("mp3", lambda f: subprocess.Popen(["xdg-open", f]))

    def open_as_video(self):
        self.safe_open("mp4", lambda f: subprocess.Popen(["xdg-open", f]))

    def open_as_image(self):
        try:
            img = Image.open(io.BytesIO(self.decrypted_data))
            img.show()
        except Exception:
            pass

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dummy test content (replace this with actual decrypted data)
    with open("example.pdf", "rb") as f:  # Replace with any test file
        decrypted_bytes = f.read()

    viewer = FileViewer(decrypted_bytes)
    sys.exit(app.exec())
