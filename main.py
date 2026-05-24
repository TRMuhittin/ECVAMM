# main.py
import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from locale.locale_manager import LocaleManager

def main():
    LocaleManager()
    app = QApplication(sys.argv)

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        font_family = config.get("font_family", "")
        font_size = config.get("font_size", 13)
        if font_family:
            app.setFont(QFont(font_family, font_size))
    except Exception:
        pass

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
