# ui/mod_settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QLabel, QPushButton,
    QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from locale.locale_manager import tr
import hjson
import os


class ModSettingsDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project

        self.setWindowTitle(tr("mod_settings.title"))
        self.setMinimumSize(600, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #181825;
                color: #cdd6f4;
            }
            QScrollArea {
                background-color: #181825;
                border: none;
            }
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #a6e3a1;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
                background: transparent;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        self._load_mod_hjson()
        self._build_ui()

    def _load_mod_hjson(self):
        self.mod_data = {}
        mod_hjson_path = os.path.join(self.project.path, "mod.hjson")
        try:
            with open(mod_hjson_path, "r", encoding="utf-8") as f:
                self.mod_data = hjson.load(f)
        except Exception:
            self.mod_data = {}

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SOL PANEL ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_layout.setSpacing(12)

        title = QLabel(tr("mod_settings.title"))
        title.setStyleSheet("color: #a6e3a1; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        form_container = QWidget()
        form = QVBoxLayout(form_container)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(0)

        basic_w = QWidget()
        basic_form = QFormLayout(basic_w)
        basic_form.setSpacing(10)
        basic_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setText(self.mod_data.get("name", ""))
        self.name_input.setPlaceholderText("my-mod")
        basic_form.addRow(tr("new_mod.mod_id"), self.name_input)

        self.display_name_input = QLineEdit()
        self.display_name_input.setText(self.mod_data.get("displayName", ""))
        self.display_name_input.setPlaceholderText("My Mod")
        basic_form.addRow(tr("new_mod.display_name"), self.display_name_input)

        self.author_input = QLineEdit()
        self.author_input.setText(self.mod_data.get("author", ""))
        self.author_input.setPlaceholderText("YourName")
        basic_form.addRow(tr("new_mod.author"), self.author_input)

        self.description_input = QLineEdit()
        self.description_input.setText(self.mod_data.get("description", ""))
        self.description_input.setPlaceholderText("A cool Mindustry mod")
        basic_form.addRow(tr("new_mod.description"), self.description_input)

        self.version_input = QLineEdit()
        self.version_input.setText(self.mod_data.get("version", "1.0"))
        basic_form.addRow(tr("new_mod.version"), self.version_input)

        self.min_version_input = QLineEdit()
        self.min_version_input.setText(str(self.mod_data.get("minGameVersion", "157")))
        basic_form.addRow(tr("new_mod.min_game_version"), self.min_version_input)

        form.addWidget(basic_w)
        form.addStretch()

        scroll.setWidget(form_container)
        left_layout.addWidget(scroll)

        save_btn = QPushButton(tr("mod_settings.save"))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1; color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        save_btn.setFixedHeight(36)
        save_btn.clicked.connect(self._save)
        left_layout.addWidget(save_btn)

        # ── SAĞ PANEL (bilgi) ──
        right = QWidget()
        right.setFixedWidth(220)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        info_title = QLabel(tr("mod_settings.info"))
        info_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        right_layout.addWidget(info_title)

        mod_path = self.project.path
        path_label = QLabel(mod_path)
        path_label.setWordWrap(True)
        path_label.setStyleSheet("color: #585b70; font-size: 11px;")
        right_layout.addWidget(path_label)

        right_layout.addStretch()

        root.addWidget(left, stretch=1)
        root.addWidget(right)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, tr("dialog.error"), tr("new_mod.error_empty"))
            return
        if " " in name:
            QMessageBox.warning(self, tr("dialog.error"), tr("new_mod.error_spaces"))
            return

        self.mod_data["name"] = name
        self.mod_data["displayName"] = self.display_name_input.text().strip()
        self.mod_data["author"] = self.author_input.text().strip()
        self.mod_data["description"] = self.description_input.text().strip()
        self.mod_data["version"] = self.version_input.text().strip()
        self.mod_data["minGameVersion"] = self.min_version_input.text().strip()

        mod_hjson_path = os.path.join(self.project.path, "mod.hjson")
        try:
            with open(mod_hjson_path, "w", encoding="utf-8") as f:
                hjson.dump(self.mod_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), str(e))
            return

        self.project.name = self.mod_data["name"]
        self.project.display_name = self.mod_data["displayName"]
        self.project.save()

        main_window = self.window()
        if hasattr(main_window, "bottom_bar"):
            main_window.bottom_bar.update()

        QMessageBox.information(self, tr("dialog.saved"), tr("dialog.saved_msg"))
        self.accept()
