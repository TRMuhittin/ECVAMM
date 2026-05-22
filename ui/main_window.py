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

class NewModDialog(QDialog):
    """Yeni mod oluşturma dialog'u."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Mod")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("my-mod (tdont make it blank)")

        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("My Mod")

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("YourName")

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("A cool Mindustry mod")

        self.version_input = QLineEdit("1.0")
        self.min_version_input = QLineEdit("157")

        layout.addRow("Mod ID:", self.name_input)
        layout.addRow("Display Name:", self.display_name_input)
        layout.addRow("Author:", self.author_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Version:", self.version_input)
        layout.addRow("Min Game Version:", self.min_version_input)

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
            QMessageBox.warning(self, "Error", "Mod ID cannot be empty.")
            return
        if " " in name:
            QMessageBox.warning(self, "Error", "Mod ID cannot contain spaces.")
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
        self.setWindowTitle("E.C.V.A.M.M.")
        self.resize(1280, 720)

        self._show_startup()

    def _show_startup(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("E.C.V.A.M.M.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
        """)

        sub_label2 = QLabel("Extremely Cool Very Awesome Mod Maker")
        sub_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label2.setStyleSheet("""
            font-size: 16px;
            color: #dcdcdc;
        """)

        sub_label = QLabel("Create or open a Mindustry mod to get started.")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("""
            font-size: 13px;
            color: gray;
        """)

        from PyQt6.QtWidgets import QPushButton
        btn_new = QPushButton("New Mod")
        btn_open = QPushButton("Open Mod")
        btn_setting = QPushButton("Settings")
        btn_new.setFixedWidth(200)
        btn_open.setFixedWidth(200)
        btn_setting.setFixedWidth(200)

        btn_new.clicked.connect(self._new_mod)
        btn_open.clicked.connect(self._open_mod)
        btn_setting.clicked.connect(lambda: QMessageBox.critical(
                self, "Error",
                " It will added soon "
        ))

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
                self, "Error",
                " It will added soon "
        ))

        btn_credits.clicked.connect(lambda: InfoDialog().exec())


        bottom_layout.addWidget(btn_discord)
        bottom_layout.addWidget(btn_github)
        bottom_layout.addWidget(btn_credits)
        bottom_layout.addWidget(btn_docs)
        
        btn_discord.setToolTip("Join our Discord server")
        btn_github.setToolTip("Open GitHub repository")
        btn_credits.setToolTip("Credits")
        btn_docs.setToolTip("Documentation")
        btn_new.setToolTip("Create a new mod")
        btn_open.setToolTip("Open a mod for edit")
        
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
        

    def _new_mod(self):

        base_path = QFileDialog.getExistingDirectory(self, "Select folder to create mod in")
        if not base_path:
            return


        dialog = NewModDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        mod_info = dialog.get_mod_info()
        project = create_new_project(base_path, mod_info)

        if project is None:
            QMessageBox.critical(self, "Error", "Mod could not be created.")
            return

        self.project = project
        self._load_main_ui()

    def _open_mod(self):
        path = QFileDialog.getExistingDirectory(self, "Select mod folder")
        if not path:
            return

        project = Project()
        if not project.load(path):
            QMessageBox.critical(
                self, "Error",
                "This folder is not a valid Ecvamm mod.\n"
                "Only mods created with Ecvamm can be opened."
            )
            return

        self.project = project
        self._load_main_ui()

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
        }

        editor_class = editors.get(content_type)
        if editor_class is None:
            QMessageBox.information(self, "Coming Soon", f"{content_type} editor is not available yet.")
            return

        self.editor_window = QWidget()
        self.editor_window.setWindowTitle(f"{content_type.capitalize()} Editor — {content.get('name', 'Unnamed')}")
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

        self.setWindowTitle("Credits")
        self.setFixedSize(250, 120)

        layout = QVBoxLayout()

        text = QLabel("Made by Kaviundurs\nThe Ecvamm\nI did here for other updates.")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(text)
        self.setLayout(layout)
        


