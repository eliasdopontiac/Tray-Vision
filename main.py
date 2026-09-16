import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.ui.main_window import MainWindow

def load_qss(app: QApplication, qss_file: str):
    if os.path.exists(qss_file):
        with open(qss_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet {qss_file} not found.")

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Load QSS
    load_qss(app, "app/styles/light_blue.qss")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
