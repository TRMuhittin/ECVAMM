# ui/grid_view.py
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout,
    QVBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from core.project import Project


CONTENT_TYPE_COLORS = {
    "Item":         "#a6e3a1",
    "Floor":        "#89b4fa",
    "Wall":         "#b4befe",
    "Turret":       "#f38ba8",
    "Weapon":       "#fab387",
    "Bullet":       "#f9e2af",
    "Unit":         "#cba6f7",
    "Liquid":       "#89dceb",
    "Crafter":      "#a6e3a1",
    "Conveyor":     "#94e2d5",
    "StatusEffect": "#eba0ac",
    "Weather":      "#89b4fa",
}


class ContentCard(QFrame):
    """Grid'deki her içerik için kart."""
    def __init__(self, content: dict, parent=None):
        super().__init__(parent)
        self.content = content
        self.setFixedSize(120, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        color = CONTENT_TYPE_COLORS.get(content.get("type", ""), "#585b70")

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Sprite önizleme alanı
        self.sprite_label = QLabel()
        self.sprite_label.setFixedSize(64, 64)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setStyleSheet(f"""
            background-color: #181825;
            border-radius: 4px;
            border: 1px solid #313244;
        """)

        # Sprite varsa göster
        sprite_path = content.get("sprite", "")
        if sprite_path:
            pixmap = QPixmap(sprite_path).scaled(
                56, 56,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.sprite_label.setPixmap(pixmap)
        else:
            self.sprite_label.setText("?")
            self.sprite_label.setStyleSheet(
                self.sprite_label.styleSheet() +
                "color: #585b70; font-size: 24px;"
            )

        # İçerik adı
        name_label = QLabel(content.get("name", "Unnamed"))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: #cdd6f4; font-size: 11px; border: none;")

        # Tip etiketi
        type_label = QLabel(content.get("type", "Unknown"))
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_label.setStyleSheet(f"""
            color: {color};
            font-size: 10px;
            font-weight: bold;
            border: none;
        """)

        layout.addWidget(self.sprite_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(type_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_editor()

    def _open_editor(self):
        from PyQt6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, "open_editor"):
                widget.open_editor(self.content)
                break


class GridView(QWidget):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setStyleSheet("background-color: #181825;")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #181825;
            }
            QScrollBar:vertical {
                background: #1e1e2e;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #45475a;
                border-radius: 4px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: #181825;")

        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(24, 24, 24, 24)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.container)
        outer_layout.addWidget(self.scroll)

        self.refresh()

    def refresh(self):
        """Projedeki tüm içerikleri grid'e yükler."""
        # Mevcut kartları temizle
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        contents = self.project.contents

        if not contents:
            empty_label = QLabel("No content yet.\nUse '+ Add Content' to get started.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #585b70; font-size: 14px;")
            self.grid_layout.addWidget(empty_label, 0, 0)
            return

        columns = 8
        for i, content in enumerate(contents):
            card = ContentCard(content)
            self.grid_layout.addWidget(card, i // columns, i % columns)
