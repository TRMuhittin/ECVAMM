# ui/settings.py
from PyQt6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QComboBox, QSpinBox, QCheckBox,
    QPushButton, QFontComboBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from locale.locale_manager import LocaleManager, tr, _read_config, _write_config


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.locale = LocaleManager()
        self.config = _read_config()
        self.language_changed = False

        self.setWindowTitle(tr("settings.title"))
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #181825;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
                background: transparent;
            }
            QListWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #45475a;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QComboBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::item {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QComboBox::item:selected {
                background-color: #313244;
            }
            QSpinBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:focus {
                border: 1px solid #a6e3a1;
            }
            QCheckBox {
                color: #cdd6f4;
                font-size: 13px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #313244;
                border-radius: 3px;
                background-color: #1e1e2e;
            }
            QCheckBox::indicator:checked {
                background-color: #a6e3a1;
                border: 1px solid #a6e3a1;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # ── Sol: Kategori listesi ──
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(160)
        self.category_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        categories = [
            ("settings.general", "⚙"),
            ("settings.editor", "✏"),
            ("settings.appearance", "🎨"),
            ("settings.about", "ℹ"),
        ]
        self._category_keys = []
        for key, icon in categories:
            item = QListWidgetItem(f"{icon}  {tr(key)}")
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.category_list.addItem(item)
            self._category_keys.append(key)

        # ── Sağ: Stacked panel ──
        self.stack = QStackedWidget()

        self._pages = {}
        for key in self._category_keys:
            page = self._create_page(key)
            self._pages[key] = page
            self.stack.addWidget(page)

        self.category_list.currentRowChanged.connect(self.stack.setCurrentIndex)

        root.addWidget(self.category_list)
        right_column = QVBoxLayout()
        right_column.setSpacing(16)
        right_column.addWidget(self.stack, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_save = QPushButton(tr("settings.save"))
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1; color: #1e1e2e;
                border: none; border-radius: 4px;
                padding: 6px 24px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        btn_cancel = QPushButton(tr("settings.cancel"))
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #45475a; color: #cdd6f4;
                border: none; border-radius: 4px;
                padding: 6px 16px; font-size: 13px;
            }
            QPushButton:hover { background-color: #585b70; }
        """)
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        right_column.addLayout(btn_layout)

        root.addLayout(right_column)

        self.category_list.setCurrentRow(0)

    def _create_page(self, key: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        if key == "settings.general":
            layout.addWidget(QLabel(tr("settings.general")))

            lang_layout = QHBoxLayout()
            lang_layout.setSpacing(8)
            lang_label = QLabel(tr("settings.language") + ":")
            lang_label.setFixedWidth(100)
            self.lang_combo = QComboBox()
            available = self.locale.available_languages()
            current_lang = self.locale.get_language()
            selected_idx = 0
            for i, (code, name) in enumerate(available):
                self.lang_combo.addItem(f"{name} ({code})", code)
                if code == current_lang:
                    selected_idx = i
            self.lang_combo.setCurrentIndex(selected_idx)
            lang_layout.addWidget(lang_label)
            lang_layout.addWidget(self.lang_combo, stretch=1)
            layout.addLayout(lang_layout)

            font_layout = QHBoxLayout()
            font_layout.setSpacing(8)
            font_label = QLabel(tr("settings.font_family") + ":")
            font_label.setFixedWidth(100)
            self.font_combo = QFontComboBox()
            current_font = self.config.get("font_family", "")
            if current_font:
                idx = self.font_combo.findText(current_font)
                if idx >= 0:
                    self.font_combo.setCurrentIndex(idx)
            font_layout.addWidget(font_label)
            font_layout.addWidget(self.font_combo, stretch=1)
            layout.addLayout(font_layout)

            size_layout = QHBoxLayout()
            size_layout.setSpacing(8)
            size_label = QLabel(tr("settings.font_size") + ":")
            size_label.setFixedWidth(100)
            self.font_size_spin = QSpinBox()
            self.font_size_spin.setRange(8, 32)
            self.font_size_spin.setValue(self.config.get("font_size", 13))
            size_layout.addWidget(size_label)
            size_layout.addWidget(self.font_size_spin)
            size_layout.addStretch()
            layout.addLayout(size_layout)

            # ── Startup Defaults ──
            sep = QLabel(tr("settings.startup_defaults"))
            sep.setStyleSheet("color: #a6e3a1; font-size: 14px; font-weight: bold; padding-top: 8px;")
            layout.addWidget(sep)

            def _make_sd_input(placeholder=""):
                w = QLineEdit()
                w.setPlaceholderText(placeholder)
                w.setStyleSheet("""
                    QLineEdit {
                        background-color: #1e1e2e; color: #cdd6f4;
                        border: 1px solid #313244; border-radius: 4px;
                        padding: 4px 8px; font-size: 13px;
                    }
                    QLineEdit:focus { border: 1px solid #a6e3a1; }
                """)
                return w

            sd_layout = QFormLayout()
            sd_layout.setSpacing(8)
            sd_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            self.default_author = _make_sd_input("YourName")
            self.default_author.setText(self.config.get("default_author", ""))
            sd_layout.addRow(QLabel(tr("settings.default_author") + ":"), self.default_author)

            self.default_version = _make_sd_input("1.0")
            self.default_version.setText(self.config.get("default_version", "1.0"))
            sd_layout.addRow(QLabel(tr("settings.default_version") + ":"), self.default_version)

            self.default_min_version = _make_sd_input("145")
            self.default_min_version.setText(self.config.get("default_min_version", "145"))
            sd_layout.addRow(QLabel(tr("settings.default_min_version") + ":"), self.default_min_version)

            self.default_desc = _make_sd_input("A cool Mindustry mod")
            self.default_desc.setText(self.config.get("default_desc", ""))
            sd_layout.addRow(QLabel(tr("settings.default_desc") + ":"), self.default_desc)

            layout.addLayout(sd_layout)
            layout.addStretch()

        elif key == "settings.editor":
            layout.addWidget(QLabel(tr("settings.editor")))

            self.auto_save_cb = QCheckBox(tr("settings.editor_auto_save"))
            self.auto_save_cb.setChecked(self.config.get("editor_auto_save", False))
            layout.addWidget(self.auto_save_cb)

            self.show_tooltips_cb = QCheckBox(tr("settings.editor_show_tooltips"))
            self.show_tooltips_cb.setChecked(self.config.get("editor_show_tooltips", True))
            layout.addWidget(self.show_tooltips_cb)

            self.default_values_cb = QCheckBox(tr("settings.editor_default_values"))
            self.default_values_cb.setChecked(self.config.get("editor_default_values", True))
            layout.addWidget(self.default_values_cb)

            layout.addStretch()

        elif key == "settings.appearance":
            layout.addWidget(QLabel(tr("settings.appearance")))

            theme_layout = QHBoxLayout()
            theme_layout.setSpacing(8)
            theme_label = QLabel(tr("settings.theme") + ":")
            theme_label.setFixedWidth(100)
            self.theme_combo = QComboBox()
            self.theme_combo.addItem(tr("settings.theme_dark"), "catppuccin_mocha")
            current_theme = self.config.get("theme", "catppuccin_mocha")
            idx = self.theme_combo.findData(current_theme)
            if idx >= 0:
                self.theme_combo.setCurrentIndex(idx)
            theme_layout.addWidget(theme_label)
            theme_layout.addWidget(self.theme_combo, stretch=1)
            layout.addLayout(theme_layout)

            layout.addStretch()

        elif key == "settings.about":
            layout.addWidget(QLabel(tr("settings.app_name")))
            layout.addWidget(QLabel(tr("settings.app_version") + ": Beta 0.1.2"))
            layout.addStretch()

        return page

    def accept(self):
        lang = self.lang_combo.currentData()
        font_family = self.font_combo.currentFont().family()
        font_size = self.font_size_spin.value()

        self.config["language"] = lang
        self.config["font_family"] = font_family
        self.config["font_size"] = font_size
        self.config["editor_auto_save"] = self.auto_save_cb.isChecked()
        self.config["editor_show_tooltips"] = self.show_tooltips_cb.isChecked()
        self.config["editor_default_values"] = self.default_values_cb.isChecked()
        self.config["theme"] = self.theme_combo.currentData()
        self.config["default_author"] = self.default_author.text().strip()
        self.config["default_version"] = self.default_version.text().strip()
        self.config["default_min_version"] = self.default_min_version.text().strip()
        self.config["default_desc"] = self.default_desc.text().strip()

        _write_config(self.config)

        if lang != self.locale.get_language():
            self.locale.set_language(lang)
            self.language_changed = True

        app = QApplication.instance()
        if app:
            app.setFont(QFont(font_family, font_size))

        super().accept()
