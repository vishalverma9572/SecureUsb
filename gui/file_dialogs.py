from PyQt6.QtWidgets import QFileDialog

def select_file():
    """Opens a file selection dialog and returns the chosen file path."""
    file_path, _ = QFileDialog.getOpenFileName(None, "Select File", "", "All Files (*)")
    return file_path

def save_file():
    """Opens a file save dialog and returns the chosen file path."""
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "Encrypted Files (*.enc)")
    return file_path
