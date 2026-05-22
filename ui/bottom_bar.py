# ui/bottom_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from core.project import Project


class BottomBar(QWidget):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setFixedHeight(28)
        self.setStyleSheet("""
            border-top: 1px solid #313244;
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        self.project_label = QLabel(project.display_name or project.name)
        self.project_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.project_label.setStyleSheet("color: #dcdcdc; font-size: 12px;")

        self.content_count_label = QLabel()
        self.content_count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.content_count_label.setStyleSheet("color: #dcdcdc; font-size: 11px;")

        self._update_count()

        layout.addSpacing(12)
        layout.addWidget(self.project_label)
        layout.addStretch()
        layout.addWidget(self.content_count_label)

    def _update_count(self):
        count = len(self.project.contents)
        self.content_count_label.setText(f"{count} content{'s' if count != 1 else ''}")

    def update(self):
        self.project_label.setText(self.project.display_name or self.project.name)
        self._update_count()
