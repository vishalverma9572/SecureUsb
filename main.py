import sys
from PyQt6.QtWidgets import QApplication
from gui.usb_window import USBDeviceWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = USBDeviceWindow()
    window.show()
    sys.exit(app.exec())
