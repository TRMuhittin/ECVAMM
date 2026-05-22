# ui/top_bar.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    QMenu, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from core.project import Project


class TopBar(QWidget):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setFixedHeight(48)
        self.setStyleSheet("background-color: #1e1e2e; border-bottom: 1px solid #313244;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # --- Sol taraf: File menüsü ---
        self.btn_file = QPushButton("File")
        self.btn_file.setFixedWidth(80)
        self.btn_file.clicked.connect(self._open_file_menu)

        # --- Orta: Add butonu ---
        self.btn_add = QPushButton("+ Add Content")
        self.btn_add.setFixedWidth(140)
        self.btn_add.clicked.connect(self._open_add_menu)
        
        self.btn_cha = QPushButton("Change Content")
        self.btn_cha.setFixedWidth(140)
        self.btn_cha.clicked.connect(lambda: QMessageBox.information(self, "Coming Soon", "Coming Soon"))

        # --- Sağ taraf: Build / Export ---
        self.btn_build = QPushButton("Build .zip")
        self.btn_build.setFixedWidth(100)
        self.btn_build.clicked.connect(self._build_zip)

        layout.addWidget(self.btn_file)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_cha)
        layout.addStretch()
        layout.addWidget(self.btn_build)

        self._apply_button_style()

    def _apply_button_style(self):
        style = """
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
        """
        for btn in [self.btn_file, self.btn_add, self.btn_build, self.btn_cha]:
            btn.setStyleSheet(style)

    def _open_file_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
            }
            QMenu::item:selected {
                background-color: #313244;
            }
        """)

        action_save = menu.addAction("Save")
        action_open = menu.addAction("Open Mod")
        menu.addSeparator()
        action_mod_settings = menu.addAction("Mod Settings")
        menu.addSeparator()
        settings = menu.addAction("Preferences")

        action_save.triggered.connect(self._save)
        action_open.triggered.connect(self._open_mod)
        action_mod_settings.triggered.connect(self._mod_settings)
        settings.triggered.connect(self._mod_settings)

        menu.exec(self.btn_file.mapToGlobal(self.btn_file.rect().bottomLeft()))

    def _open_add_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
            }
            QMenu::item:selected {
                background-color: #313244;
            }
        """)

        for content_type in [
            "Item", "Block", "Wall",
            "Turret", "Weapon", "Bullet", "Unit",
            "Liquid", "Crafter", "Conveyor",
            "Status Effect", "Weather"
        ]:
            menu.addAction(content_type)

        menu.triggered.connect(self._on_add_content)
        menu.exec(self.btn_add.mapToGlobal(self.btn_add.rect().bottomLeft()))


    def _on_add_content(self, action):
        content_type = action.text().lower().replace(" ", "_")
        new_content = {"type": content_type, "name": ""}
        main_window = self.window()
        if hasattr(main_window, "open_editor"):
            main_window.open_editor(new_content)

    def _save(self):
        if self.project.save():
            QMessageBox.information(self, "Saved", "Project Saved.")
        else:
            QMessageBox.critical(self, "Error", "Project cant be saved.")

    def _open_mod(self):
        # MainWindow'daki _open_mod'u tetikler
        main_window = self.window()
        if hasattr(main_window, "_open_mod"):
            main_window._open_mod()

    def _mod_settings(self):
        # Mod ayarları dialog'u, ilerleyen aşamada
        QMessageBox.information(self, "Coming Soon", "Settings is not ready.")

    def _build_zip(self):
        # ZIP oluşturma, ilerleyen aşamada
        QMessageBox.information(self, "Coming Soon", "Build henüz is not ready. But you can zip the file and use it like a mod.")
