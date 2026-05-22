# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
    QToolTip {
        background-color: #313244;
        color: #cdd6f4;
        border-radius: 6px;
        padding: 6px;
        font-size: 12px;
    }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
