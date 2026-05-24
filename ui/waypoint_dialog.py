from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import Qt
from core.project import Project
from locale.locale_manager import tr
import os


class WaypointDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.restored_project = None

        self.setWindowTitle(tr("waypoint.title"))
        self.setMinimumSize(520, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #181825; color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4; font-size: 13px; background: transparent;
            }
            QListWidget {
                background-color: #1e1e2e; color: #cdd6f4;
                border: 1px solid #313244; border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item { padding: 8px 12px; border-radius: 4px; }
            QListWidget::item:selected { background-color: #45475a; }
            QListWidget::item:hover { background-color: #313244; }
            QPushButton {
                background-color: #313244; color: #cdd6f4;
                border: none; border-radius: 4px;
                padding: 6px 16px; font-size: 13px;
            }
            QPushButton:hover { background-color: #45475a; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel(tr("waypoint.list_title"))
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #a6e3a1;")
        root.addWidget(title)

        self.list_widget = QListWidget()
        self._populate()
        root.addWidget(self.list_widget, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_create = QPushButton(tr("waypoint.create"))
        btn_create.clicked.connect(self._create)

        btn_restore = QPushButton(tr("waypoint.restore"))
        btn_restore.clicked.connect(self._restore)

        btn_clean = QPushButton(tr("waypoint.clean"))
        btn_clean.clicked.connect(self._clean)

        btn_close = QPushButton(tr("settings.cancel"))
        btn_close.clicked.connect(self.reject)

        btn_row.addWidget(btn_create)
        btn_row.addWidget(btn_restore)
        btn_row.addWidget(btn_clean)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _populate(self):
        self.list_widget.clear()
        self._waypoints = Project.list_waypoints(self.project.path)
        if not self._waypoints:
            item = QListWidgetItem(tr("waypoint.none"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return
        for wp in self._waypoints:
            from datetime import datetime
            dt = datetime.fromtimestamp(wp["mtime"])
            label = f'{wp["ts"]}  —  {dt.strftime("%Y-%m-%d %H:%M:%S")}'
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, wp["ts"])
            self.list_widget.addItem(item)

    def _create(self):
        ts = self.project.save_waypoint()
        if ts:
            self._populate()
            self.list_widget.setCurrentRow(0)
        else:
            QMessageBox.warning(self, tr("dialog.error"), tr("waypoint.create_failed"))

    def _restore(self):
        current = self.list_widget.currentItem()
        if not current or not current.data(Qt.ItemDataRole.UserRole):
            return
        ts = current.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, tr("waypoint.restore_confirm_title"),
            tr("waypoint.restore_confirm").format(ts=ts),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.restored_project = Project.load_waypoint(self.project.path, ts)
        if self.restored_project:
            self.accept()
        else:
            QMessageBox.warning(self, tr("dialog.error"), tr("waypoint.restore_failed"))

    def _clean(self):
        count = len(self._waypoints)
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
        self._populate()
