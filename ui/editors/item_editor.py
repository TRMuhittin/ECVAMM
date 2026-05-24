# ui/editors/item_editor.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QFormLayout, QLineEdit, QLabel,
    QPushButton, QFileDialog, QSpinBox,
    QDoubleSpinBox, QScrollArea, QColorDialog,
    QCheckBox, QMessageBox, QMenu, QApplication,
    QCompleter
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QColor, QAction
import os
import hjson
from locale.locale_manager import tr


MINDUSTRY_ITEMS = [
    "copper", "lead", "graphite", "metaglass", "titanium",
    "thorium", "plastanium", "phase-fabric", "surge-alloy",
    "silicon", "pyratite", "blast-compound", "spore-pod",
    "beryllium", "tungsten", "oxide", "carbide",
    "fissile-matter", "sand", "scrap", "coal",  
]


OPTIONAL_PROPERTIES = {
    "hardness":         ("int",    0,    10,   0),
    "cost":             ("float",  0.0,  9999.0, 1.0),
    "explosiveness":    ("float",  0.0,  9999.0, 0.0),
    "flammability":     ("float",  0.0,  9999.0, 0.0),
    "radioactivity":    ("float",  0.0,  9999.0, 0.0),
    "charge":           ("float",  0.0,  9999.0, 0.0),
    "healthScaling":    ("float",  0.0,  9999.0, 0.0),
    "frames":           ("int",    0,    9999,   0),
    "transitionFrames": ("int",    0,    9999,   0),
    "frameTime":        ("float",  0.0,  9999.0, 5.0),
    "lowPriority":      ("bool",   None, None,   False),
    "buildable":        ("bool",   None, None,   True),
    "hidden":           ("bool",   None, None,   False),
    "research":         ("str",    None, None,   ""),
}

PROPERTY_LABELS = {
    "hardness":         "Hardness",
    "cost":             "Cost",
    "explosiveness":    "Explosiveness",
    "flammability":     "Flammability",
    "radioactivity":    "Radioactivity",
    "charge":           "Charge",
    "healthScaling":    "Health Scaling",
    "frames":           "Frames",
    "transitionFrames": "Transition Frames",
    "frameTime":        "Frame Time",
    "lowPriority":      "Low Priority",
    "buildable":        "Buildable",
    "hidden":           "Hidden",
    "research":         "Research Parent",
}


class ItemEditor(QWidget):
    def __init__(self, content: dict, project, parent=None):
        super().__init__(parent)
        self.content = content
        self.project = project
        self.sprite_path = content.get("sprite", "")
        self.main_window = None
        

        # Aktif opsiyonel alanları takip et: key -> widget
        self.active_props: dict = {}

        self.setStyleSheet("""
            QWidget          { background-color: #181825; color: #cdd6f4; }
            QScrollArea      { background-color: #181825; border: none; }
            QLineEdit        { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 4px 8px; font-size: 13px; }
            QLineEdit:focus  { border: 1px solid #a6e3a1; }
            QAbstractSpinBox { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 4px 8px; font-size: 13px; }
            QAbstractSpinBox:focus { border: 1px solid #a6e3a1; }
            QCheckBox        { color: #cdd6f4; background-color: transparent; font-size: 13px; }
            QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #313244; border-radius: 3px; background-color: #1e1e2e; }
            QCheckBox::indicator:checked { background-color: #a6e3a1; border: 1px solid #a6e3a1; }
            QLabel           { background-color: transparent; color: #cdd6f4; font-size: 13px; }
            QMenu            { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; }
            QMenu::item:selected { background-color: #313244; }
        """)

        # Ana layout: sol + sağ
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SOL PANEL ──────────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_layout.setSpacing(12)

        title = QLabel(tr("item_editor.title"))
        title.setStyleSheet("color: #a6e3a1; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(0)

        # Zorunlu form
        basic_form_widget = QWidget()
        self.basic_form = QFormLayout(basic_form_widget)
        self.basic_form.setSpacing(10)
        self.basic_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input        = self._make_input(tr("item_editor.placeholder_name", "my-item"))
        self.display_name_input = self._make_input(tr("item_editor.placeholder_display", "My Item"))
        self.description_input = self._make_input(tr("item_editor.placeholder_desc", "Description"))

        self.color_value = content.get("color", "000000")
        self.color_btn = QPushButton(f"  #{self.color_value}")
        self.color_btn.setStyleSheet(self._color_btn_style(self.color_value))
        self.color_btn.clicked.connect(self._pick_color)

        self.basic_form.addRow(self._make_label("name"),        self.name_input)
        self.basic_form.addRow(self._make_label("displayName"), self.display_name_input)
        self.basic_form.addRow(self._make_label("description"), self.description_input)
        self.basic_form.addRow(self._make_label("color"),       self.color_btn)

        self.form_layout.addWidget(basic_form_widget)

        # Opsiyonel alanlar bölümü
        sep = QLabel(tr("item_editor.optional_separator"))
        sep.setStyleSheet("color: #585b70; font-size: 11px; padding-top: 12px;")
        self.form_layout.addWidget(sep)

        self.optional_form_widget = QWidget()
        self.optional_form = QFormLayout(self.optional_form_widget)
        self.optional_form.setSpacing(10)
        self.optional_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.addWidget(self.optional_form_widget)

        # Add Property butonu
        self.add_prop_btn = QPushButton(tr("item_editor.add_property"))
        self.add_prop_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.add_prop_btn.clicked.connect(self._open_add_prop_menu)
        self.form_layout.addWidget(self.add_prop_btn)
        self.form_layout.addStretch()

        scroll.setWidget(self.form_container)
        left_layout.addWidget(scroll)

        # Save butonu
        save_btn = QPushButton(tr("item_editor.save"))
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        save_btn.clicked.connect(self._save)
        left_layout.addWidget(save_btn)

        # ── SAĞ PANEL ─────────────────────────────────────────────
        right = QWidget()
        right.setFixedWidth(240)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        sprite_title = QLabel(tr("item_editor.sprite"))
        sprite_title.setStyleSheet("font-size: 13px; font-weight: bold;")

        self.sprite_preview = QLabel()
        self.sprite_preview.setFixedSize(180, 180)
        self.sprite_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_preview.setStyleSheet("""
            background-color: #1e1e2e;
            border: 1px solid #313244;
            border-radius: 8px;
            color: #585b70;
            font-size: 13px;
        """)
        self.sprite_preview.setText(tr("item_editor.no_sprite"))

        sprite_btn = QPushButton(tr("item_editor.load_sprite"))
        sprite_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        sprite_btn.clicked.connect(self._load_sprite)

        right_layout.addWidget(sprite_title)
        right_layout.addWidget(self.sprite_preview)
        right_layout.addWidget(sprite_btn)

        root.addWidget(left, stretch=1)
        root.addWidget(right)

        self._populate()

    # ── YARDIMCI ──────────────────────────────────────────────────

    def _make_label(self, key: str) -> QLabel:
        display = PROPERTY_LABELS.get(key, key)
        label = QLabel(f"{display}:")
        label.setStyleSheet("color: #cdd6f4; font-size: 13px; background: transparent;")
        tip = tr(f"tooltip.item.{key}", "")
        if tip:
            label.setToolTip(tip)
        return label

    def _make_input(self, placeholder="") -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        return w

    def _make_widget_for(self, key: str):
        ptype, mn, mx, default = OPTIONAL_PROPERTIES[key]
        if ptype == "int":
            w = QSpinBox()
            w.setRange(mn, mx)
            w.setValue(self.content.get(key, default))
        elif ptype == "float":
            w = QDoubleSpinBox()
            w.setRange(mn, mx)
            w.setDecimals(2)
            w.setValue(self.content.get(key, default))
        elif ptype == "bool":
            w = QCheckBox()
            w.setChecked(self.content.get(key, default))
        else:  # str
            w = QLineEdit()
            w.setText(str(self.content.get(key, default)))
            if key == "research":
                completer = QCompleter(MINDUSTRY_ITEMS, w)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                w.setCompleter(completer)
        return w

    def _color_btn_style(self, hex_color: str) -> str:
        light = self._is_light(hex_color)
        return f"""
            QPushButton {{
                background-color: #{hex_color};
                color: {'#000000' if light else '#ffffff'};
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
                text-align: left;
            }}
        """

    def _is_light(self, hex_color: str) -> bool:
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r * 299 + g * 587 + b * 114) / 1000 > 128
        except Exception:
            return False

    # ── OPSİYONEL ALAN YÖNETİMİ ──────────────────────────────────

    def _open_add_prop_menu(self):
        menu = QMenu(self)
        available = [k for k in OPTIONAL_PROPERTIES if k not in self.active_props]
        if not available:
            menu.addAction(tr("item_editor.all_added")).setEnabled(False)
        for key in available:
            label = PROPERTY_LABELS.get(key, key)
            action = menu.addAction(label)
            action.setData(key)
        chosen = menu.exec(self.add_prop_btn.mapToGlobal(
            self.add_prop_btn.rect().bottomLeft()
        ))
        if chosen and chosen.data():
            self._add_optional_prop(chosen.data())

    def _add_optional_prop(self, key: str):
        if key in self.active_props:
            return

        widget = self._make_widget_for(key)
        label  = self._make_label(key)

        # Sağ tarafta widget + X butonu
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)
        row_layout.addWidget(widget, stretch=1)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #eba0ac; }
        """)
        remove_btn.clicked.connect(lambda: self._remove_optional_prop(key))
        row_layout.addWidget(remove_btn)

        self.optional_form.addRow(label, row_widget)
        self.active_props[key] = widget

    def _remove_optional_prop(self, key: str):
        if key not in self.active_props:
            return
        widget = self.active_props.pop(key)
        # Form'dan ilgili satırı bul ve sil
        for i in range(self.optional_form.rowCount()):
            item = self.optional_form.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if item and item.widget():
                row_w = item.widget()
                # row_widget içindeki asıl widget'ı bul
                layout = row_w.layout()
                if layout and layout.count() > 0:
                    if layout.itemAt(0).widget() is widget:
                        self.optional_form.removeRow(i)
                        break
        self.content.pop(key, None)

    # ── VERİ ──────────────────────────────────────────────────────

    def _populate(self):
        self.name_input.setText(self.content.get("name", ""))
        self.display_name_input.setText(self.content.get("displayName", ""))
        self.description_input.setText(self.content.get("description", ""))

        # Mevcut opsiyonel alanları yükle
        for key in OPTIONAL_PROPERTIES:
            if key in self.content:
                self._add_optional_prop(key)

        if self.sprite_path:
            self._update_sprite_preview(self.sprite_path)

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(f"#{self.color_value}"), self)
        if color.isValid():
            self.color_value = color.name().lstrip("#")
            self.color_btn.setText(f"  #{self.color_value}")
            self.color_btn.setStyleSheet(self._color_btn_style(self.color_value))

    def _load_sprite(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Sprite", "", "Images (*.png)")
        if path:
            self._sprite_source = path
            self._update_sprite_preview(path)

    def _update_sprite_preview(self, path: str):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.sprite_preview.setPixmap(
                pixmap.scaled(170, 170,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
            )
            self.sprite_preview.setText("")

    def _get_prop_value(self, key: str):
        w = self.active_props[key]
        if isinstance(w, QCheckBox):
            return w.isChecked()
        elif isinstance(w, QSpinBox):
            return w.value()
        elif isinstance(w, QDoubleSpinBox):
            return w.value()
        else:
            return w.text().strip()

    def _save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, tr("dialog.error"), tr("item_editor.error_empty_name"))
            return

        item_name = self.name_input.text().strip()

        self.content["type"]        = "item"
        self.content["name"]        = item_name
        self.content["displayName"] = self.display_name_input.text().strip()
        self.content["description"] = self.description_input.text().strip()
        self.content["color"]       = self.color_value

        # Sprite'ı doğru konuma kaydet
        if hasattr(self, "_sprite_source") and self._sprite_source:
            import shutil
            sprite_dir = os.path.join(self.project.path, "sprites", "items")
            os.makedirs(sprite_dir, exist_ok=True)
            dest = os.path.join(sprite_dir, f"{item_name}.png")
            shutil.copy2(self._sprite_source, dest)
            self.sprite_path = dest
        self.content["sprite"] = self.sprite_path

        # Opsiyonel alanlar
        for key in list(self.active_props.keys()):
            self.content[key] = self._get_prop_value(key)

        # Research ayrıştır
        research_parent = self.content.pop("research", None)

        # Projeye ekle veya güncelle
        found = False
        for i, c in enumerate(self.project.contents):
            if c is self.content:
                self.project.contents[i] = self.content
                found = True
                break
        if not found:
            self.project.contents.append(self.content)

        self.project.save()

        # HJSON yaz
        items_dir = os.path.join(self.project.path, "content", "items")
        os.makedirs(items_dir, exist_ok=True)

        hjson_data = {"type": "item", "name": self.content["name"],
                      "color": self.content["color"]}

        for key in OPTIONAL_PROPERTIES:
            if key in self.content and key != "research":
                hjson_data[key] = self.content[key]

        if research_parent:
            hjson_data["research"] = research_parent
            self.content["research"] = research_parent

        hjson_path = os.path.join(items_dir, f"{self.content['name']}.hjson")
        with open(hjson_path, "w", encoding="utf-8") as f:
            hjson.dump(hjson_data, f, ensure_ascii=False, indent=2)

        if self.main_window and hasattr(self.main_window, "grid_view"):
            self.main_window.grid_view.refresh()
        if self.main_window and hasattr(self.main_window, "editor_window"):
            self.main_window.editor_window.setWindowTitle(
                tr("editor.window_title").format(type="Item", name=self.content["name"])
            )


