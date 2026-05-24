# ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize, QUrl
from core.project import Project, create_new_project
from PyQt6.QtGui import (
    QIcon,
    QDesktopServices,
)
from locale.locale_manager import tr, _read_config

class NewModDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("new_mod.title"))
        self.setMinimumWidth(400)

        config = _read_config()

        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(tr("new_mod.placeholder_id"))

        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText(tr("new_mod.placeholder_display"))

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText(tr("new_mod.placeholder_author"))
        self.author_input.setText(config.get("default_author", ""))

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(tr("new_mod.placeholder_desc"))
        self.description_input.setText(config.get("default_desc", ""))

        self.version_input = QLineEdit(config.get("default_version", "1.0"))
        self.min_version_input = QLineEdit(config.get("default_min_version", "145"))

        layout.addRow(tr("new_mod.mod_id"), self.name_input)
        layout.addRow(tr("new_mod.display_name"), self.display_name_input)
        layout.addRow(tr("new_mod.author"), self.author_input)
        layout.addRow(tr("new_mod.description"), self.description_input)
        layout.addRow(tr("new_mod.version"), self.version_input)
        layout.addRow(tr("new_mod.min_game_version"), self.min_version_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, tr("dialog.error"), tr("new_mod.error_empty"))
            return
        if " " in name:
            QMessageBox.warning(self, tr("dialog.error"), tr("new_mod.error_spaces"))
            return
        self.accept()

    def get_mod_info(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "displayName": self.display_name_input.text().strip(),
            "author": self.author_input.text().strip(),
            "description": self.description_input.text().strip(),
            "version": self.version_input.text().strip(),
            "minGameVersion": self.min_version_input.text().strip(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project: Project | None = None
        self.setWindowTitle(tr("app.window_title"))
        self.resize(1280, 720)

        self._show_startup()

    def _show_startup(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(tr("app.title"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
        """)

        sub_label2 = QLabel(tr("app.subtitle"))
        sub_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label2.setStyleSheet("""
            font-size: 16px;
            color: #dcdcdc;
        """)

        sub_label = QLabel(tr("app.description"))
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("""
            font-size: 13px;
            color: gray;
        """)

        from PyQt6.QtWidgets import QPushButton
        btn_new = QPushButton(tr("startup.new_mod"))
        btn_open = QPushButton(tr("startup.open_mod"))
        btn_setting = QPushButton(tr("startup.settings"))
        btn_new.setFixedWidth(200)
        btn_open.setFixedWidth(200)
        btn_setting.setFixedWidth(200)

        btn_new.clicked.connect(self._new_mod)
        btn_open.clicked.connect(self._open_mod)
        btn_setting.clicked.connect(self._open_settings)

        layout.addWidget(label)
        layout.addWidget(sub_label2)
        layout.addWidget(sub_label)
        layout.addSpacing(12)
        layout.addWidget(btn_new, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_open, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_setting, alignment=Qt.AlignmentFlag.AlignCenter)
        
        bottom_layout = QHBoxLayout()
        
        btn_discord = QPushButton()
        btn_github = QPushButton()
        btn_credits = QPushButton()
        btn_docs = QPushButton()
        
        for btn in [btn_discord, btn_github, btn_credits, btn_docs]:
            btn.setFixedSize(41, 41)
        
        btn_discord.setIcon(QIcon("assets/icons/discord.svg"))
        btn_github.setIcon(QIcon("assets/icons/github.svg"))
        btn_credits.setIcon(QIcon("assets/icons/about.svg"))
        btn_docs.setIcon(QIcon("assets/icons/docs.svg"))
        
        for btn in [btn_discord, btn_github, btn_credits, btn_docs]:
            btn.setIconSize(QSize(28, 28))


        btn_discord.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://discord.gg/xrbQZ3JkJH")
        ))

        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/USERNAME/REPO")
        ))

        btn_docs.clicked.connect(lambda: QMessageBox.critical(
                self, tr("dialog.error"),
                tr("dialog.not_ready")
        ))

        btn_credits.clicked.connect(lambda: InfoDialog().exec())


        bottom_layout.addWidget(btn_discord)
        bottom_layout.addWidget(btn_github)
        bottom_layout.addWidget(btn_credits)
        bottom_layout.addWidget(btn_docs)
        
        btn_discord.setToolTip(tr("tooltip.discord"))
        btn_github.setToolTip(tr("tooltip.github"))
        btn_credits.setToolTip(tr("tooltip.credits"))
        btn_docs.setToolTip(tr("tooltip.docs"))
        btn_new.setToolTip(tr("tooltip.new_mod"))
        btn_open.setToolTip(tr("tooltip.open_mod"))
        
        self.setStyleSheet("""
        QToolTip {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #444;
            padding: 4px;
        }
        """)
        
        bottom_layout.setSpacing(12)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        layout.addSpacing(0)
        layout.addLayout(bottom_layout)
        

    def _open_settings(self):
        from ui.settings import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
        if dialog.language_changed:
            self._refresh_ui()

    def _refresh_ui(self):
        if self.project is None:
            self._show_startup()
        else:
            self._load_main_ui()

    def _new_mod(self):

        base_path = QFileDialog.getExistingDirectory(self, tr("select.folder_create"))
        if not base_path:
            return


        dialog = NewModDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        mod_info = dialog.get_mod_info()
        project = create_new_project(base_path, mod_info)

        if project is None:
            QMessageBox.critical(self, tr("dialog.error"), tr("error.mod_create_failed"))
            return

        self.project = project
        self._load_main_ui()

    def _open_mod(self):
        path = QFileDialog.getExistingDirectory(self, tr("select.folder_open"))
        if not path:
            return

        from core.mod_structure import is_valid_mod
        import os

        project = Project()
        if project.load(path):
            self.project = project
            self._load_main_ui()
            return

        # Kurtarma: waypoint'ler var mı?
        from core.project import Project as P
        waypoints = P.list_waypoints(path)
        if waypoints:
            reply = QMessageBox.question(
                self, tr("dialog.recovery_title"),
                tr("dialog.recovery_waypoint_ask"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                from ui.waypoint_dialog import WaypointDialog
                dummy = P()
                dummy.path = path
                dialog = WaypointDialog(dummy, self)
                if dialog.exec() == QDialog.DialogCode.Accepted and dialog.restored_project:
                    self.project = dialog.restored_project
                    self._load_main_ui()
                    return

        # Kurtarma: mod.hjson'dan tara
        mod_hjson_path = os.path.join(path, "mod.hjson")
        if os.path.exists(mod_hjson_path):
            reply = QMessageBox.question(
                self, tr("dialog.recovery_title"),
                tr("dialog.recovery_ask"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                from core.project import recover_project
                project = recover_project(path)
                if project is not None:
                    self.project = project
                    self._load_main_ui()
                    return

        QMessageBox.critical(
            self, tr("dialog.error"),
            tr("error.invalid_mod")
        )

    def _apply_restored_project(self, project):
        self.project = project
        self._load_main_ui()
        QMessageBox.information(self, tr("dialog.saved"), tr("waypoint.restored"))

    def _load_main_ui(self):
        from ui.top_bar import TopBar
        from ui.grid_view import GridView
        from ui.bottom_bar import BottomBar

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.top_bar = TopBar(self.project)
        self.grid_view = GridView(self.project)
        self.bottom_bar = BottomBar(self.project)

        self.top_bar.delete_toggle.toggled.connect(self.grid_view.set_delete_mode)

        layout.addWidget(self.top_bar)
        layout.addWidget(self.grid_view, stretch=1)
        layout.addWidget(self.bottom_bar)
        
    def open_editor(self, content: dict):
        from ui.editors.item_editor import ItemEditor
        from ui.editors.base_block_editor import BlockEditor

        content_type = content.get("type", "")

        editors = {
            "item": ItemEditor,
            "block": BlockEditor,
            "wall": BlockEditor,
            "floor": BlockEditor,
            "turret": BlockEditor,
            "conveyor": BlockEditor,
            "crafter": BlockEditor,
        }

        editor_class = editors.get(content_type)
        if editor_class is None:
            QMessageBox.information(
                self, tr("dialog.coming_soon"),
                tr("editor.not_available").format(type=content_type)
            )
            return

        self.editor_window = QWidget()
        self.editor_window.setWindowTitle(
            tr("editor.window_title").format(
                type=content_type.capitalize(),
                name=content.get("name", tr("grid.unnamed"))
            )
        )
        self.editor_window.resize(900, 600)

        layout = QVBoxLayout(self.editor_window)
        layout.setContentsMargins(0, 0, 0, 0)
        
        editor = editor_class(content, self.project)
        editor.main_window = self 
        layout.addWidget(editor)
        
        self.editor_window.show()
        
class InfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(tr("credits.title"))
        self.setFixedSize(250, 120)

        layout = QVBoxLayout()

        text = QLabel(tr("credits.text"))
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(text)
        self.setLayout(layout)
        


