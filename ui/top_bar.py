# ui/top_bar.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    QMenu, QMessageBox, QFileDialog, QCheckBox,
    QDialog
)
from PyQt6.QtCore import Qt
from core.project import Project
from locale.locale_manager import tr
import os


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
        self.btn_file = QPushButton(tr("topbar.file"))
        self.btn_file.setFixedWidth(80)
        self.btn_file.clicked.connect(self._open_file_menu)

        # --- Orta: Add butonu ---
        self.btn_add = QPushButton(tr("topbar.add_content"))
        self.btn_add.setFixedWidth(140)
        self.btn_add.clicked.connect(self._open_add_menu)
        
        self.btn_cha = QPushButton(tr("topbar.change_content"))
        self.btn_cha.setFixedWidth(140)
        self.btn_cha.clicked.connect(lambda: QMessageBox.information(self, tr("dialog.coming_soon"), tr("dialog.coming_soon")))

        # --- Sağ taraf: Delete toggle + Build ---
        self.delete_toggle = QCheckBox(tr("topbar.delete_mode"))
        self.delete_toggle.setStyleSheet("""
            QCheckBox {
                color: #f38ba8; font-size: 12px; spacing: 4px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1px solid #313244; border-radius: 3px;
                background-color: #1e1e2e;
            }
            QCheckBox::indicator:checked {
                background-color: #f38ba8; border: 1px solid #f38ba8;
            }
        """)
        self.btn_build = QPushButton(tr("topbar.build_zip"))
        self.btn_build.setFixedWidth(100)
        self.btn_build.clicked.connect(self._build_zip)

        layout.addWidget(self.btn_file)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_cha)
        layout.addStretch()
        layout.addWidget(self.delete_toggle)
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

        action_save = menu.addAction(tr("file_menu.save"))
        action_open = menu.addAction(tr("file_menu.open_mod"))
        menu.addSeparator()
        action_mod_settings = menu.addAction(tr("file_menu.mod_settings"))
        menu.addSeparator()
        waypoints_menu = menu.addMenu(tr("file_menu.waypoints"))
        action_wp_create = waypoints_menu.addAction(tr("file_menu.wp_create"))
        action_wp_manage = waypoints_menu.addAction(tr("file_menu.wp_manage"))
        action_wp_clean = waypoints_menu.addAction(tr("file_menu.wp_clean"))
        menu.addSeparator()
        settings = menu.addAction(tr("file_menu.preferences"))

        action_save.triggered.connect(self._save)
        action_open.triggered.connect(self._open_mod)
        action_mod_settings.triggered.connect(self._mod_settings)
        action_wp_create.triggered.connect(self._create_waypoint)
        action_wp_manage.triggered.connect(self._manage_waypoints)
        action_wp_clean.triggered.connect(self._clean_waypoints)
        settings.triggered.connect(self._open_preferences)

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

        content_types = [
            ("add_menu.item", "Item"),
            ("add_menu.block", "Block"),
            ("add_menu.wall", "Wall"),
            ("add_menu.turret", "Turret"),
            ("add_menu.weapon", "Weapon"),
            ("add_menu.bullet", "Bullet"),
            ("add_menu.unit", "Unit"),
            ("add_menu.liquid", "Liquid"),
            ("add_menu.crafter", "Crafter"),
            ("add_menu.conveyor", "Conveyor"),
            ("add_menu.status_effect", "Status Effect"),
            ("add_menu.weather", "Weather"),
        ]
        for key, english in content_types:
            action = menu.addAction(tr(key, english))
            action.setData(english)

        menu.triggered.connect(self._on_add_content)
        menu.exec(self.btn_add.mapToGlobal(self.btn_add.rect().bottomLeft()))


    def _on_add_content(self, action):
        content_type = action.data().lower().replace(" ", "_")
        new_content = {"type": content_type, "name": ""}
        main_window = self.window()
        if hasattr(main_window, "open_editor"):
            main_window.open_editor(new_content)

    def _save(self):
        if self.project.save():
            QMessageBox.information(self, tr("dialog.saved"), tr("dialog.saved_msg"))
        else:
            QMessageBox.critical(self, tr("dialog.error"), tr("dialog.save_error"))

    def _open_mod(self):
        main_window = self.window()
        if hasattr(main_window, "_open_mod"):
            main_window._open_mod()

    def _mod_settings(self):
        from ui.mod_settings_dialog import ModSettingsDialog
        dialog = ModSettingsDialog(self.project, self)
        dialog.exec()

    def _open_preferences(self):
        from ui.settings import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
        if dialog.language_changed:
            main_window = self.window()
            if hasattr(main_window, "_refresh_ui"):
                main_window._refresh_ui()

    def _create_waypoint(self):
        ts = self.project.save_waypoint()
        if ts:
            QMessageBox.information(self, tr("dialog.saved"), tr("waypoint.created").format(ts=ts))
        else:
            QMessageBox.critical(self, tr("dialog.error"), tr("waypoint.create_failed"))

    def _manage_waypoints(self):
        from ui.waypoint_dialog import WaypointDialog
        dialog = WaypointDialog(self.project, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.restored_project:
            main_window = self.window()
            if hasattr(main_window, "_apply_restored_project"):
                main_window._apply_restored_project(dialog.restored_project)

    def _clean_waypoints(self):
        from core.project import Project
        wps = Project.list_waypoints(self.project.path)
        count = len(wps)
        if count <= 10:
            QMessageBox.information(self, tr("waypoint.clean_title"), tr("waypoint.clean_noop"))
            return
        reply = QMessageBox.question(
            self, tr("waypoint.clean_title"),
            tr("waypoint.clean_confirm").format(count=count - 10),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        Project.clean_waypoints(self.project.path, keep=10)
        QMessageBox.information(self, tr("dialog.saved"), tr("waypoint.clean_done"))

    def _build_zip(self):
        default_name = f"{self.project.name}.zip"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("dialog.build_title"), default_name,
            "ZIP Archive (*.zip)"
        )
        if not path:
            return

        import zipfile
        try:
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                root = self.project.path
                for dirpath, _, filenames in os.walk(root):
                    for fname in filenames:
                        full = os.path.join(dirpath, fname)
                        arcname = os.path.relpath(full, root)
                        zf.write(full, arcname)
            QMessageBox.information(self, tr("dialog.saved"), tr("dialog.build_success"))
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), f"{tr('dialog.build_failed')}\n{e}")
