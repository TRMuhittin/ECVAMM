# ui/editors/base_block_editor.py
#
# ════════════════════════════════════════════════════════════════════════════
#  YAPIYI ANLAMAK İÇİN OKUYUN
# ════════════════════════════════════════════════════════════════════════════
#
#  1. ZORUNLU ALANLAR
#     Sadece "name" ve "displayName" zorunlu.
#     Bunlar sabit, her zaman formdadır.
#
#  2. OPSİYONEL ALANLAR  →  OPTIONAL_CATEGORIES
#     Kategorilere ayrılmış sözlük. Her kategori bir başlık altında
#     "Add Property" menüsünde gruplanarak gösterilir.
#
#     Format:
#       "KATEGORİ ADI": {
#           "property_key": ("tip", min, max, default, "tooltip açıklaması"),
#       }
#
#     Desteklenen tipler:
#       "int"   → QSpinBox
#       "float" → QDoubleSpinBox
#       "bool"  → QCheckBox
#       "str"   → QLineEdit
#
#     Örnek satır:
#       "health": ("int", 0, 99999, 100, "Bloğun maksimum can puanı"),
#
#  3. LİSTE GİRDİLERİ  →  LIST_PROPERTIES
#     Birden fazla satır eklenebilen özel alanlar (örn: researchCost).
#     Her kayıt birden fazla field içerebilir.
#
#     Format:
#       "property_key": {
#           "label":   "Arayüzde görünecek başlık",
#           "tooltip": "Açıklama",
#           "fields": [
#               ("field_key", "tip", min_veya_None, max_veya_None, default, "placeholder"),
#               ...
#           ]
#       }
#
#     Desteklenen tipler: "str", "int", "float"
#
#     Örnek (researchCost):
#       "researchCost": {
#           "label": "Research Cost",
#           "tooltip": "Araştırma için gereken kaynaklar",
#           "fields": [
#               ("item",   "str", None, None, "",    "item id  (örn: copper)"),
#               ("amount", "int", 0,    99999, 0,    "miktar"),
#           ]
#       }
#
#     Yeni liste tipi eklemek için sadece LIST_PROPERTIES'e giriş yaz.
#
# ════════════════════════════════════════════════════════════════════════════


from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QFileDialog,
    QSpinBox, QDoubleSpinBox, QScrollArea, QColorDialog,
    QCheckBox, QMessageBox, QMenu, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QAction
import os
import hjson


# ── OPSİYONEL ALAN KATEGORİLERİ ─────────────────────────────────────────────
# Buraya yeni kategori veya property ekleyebilirsin.
# ("tip", min, max, default, "tooltip")

OPTIONAL_CATEGORIES: dict[str, dict[str, tuple]] = {

    "General": {
        # "property_key": ("tip", min,  max,   default, "tooltip"),
        "health":         ("int",   0, 99999,  100,   "Bloğun maksimum can puanı"),
        "size":           ("int",   1,   100,    1,   "Blok boyutu (hücre cinsinden, örn: 2 → 2x2)"),
        "armor":          ("float", 0.0, 100.0,  0.0, "Hasar azaltma yüzdesi"),
        "buildCost":      ("float", 0.0, 9999.0, 1.0, "İnşa etme maliyeti"),
        "buildTime":      ("float", 0.0, 9999.0, 0.0, "İnşa süresi (saniye)"),
        "solid":          ("bool",  None, None,  True, "Üzerinden geçilemeyen katı blok mu?"),
        "update":         ("bool",  None, None,  True, "Her tick güncelleniyor mu?"),
        "hasItems":       ("bool",  None, None,  False,"Item depolayabiliyor mu?"),
        "hasLiquids":     ("bool",  None, None,  False,"Sıvı depolayabiliyor mu?"),
        "hasPower":       ("bool",  None, None,  False,"Güç alıp verebiliyor mu?"),
    },

    "Turret": {
        # Kule (turret) bloklarına özgü alanlar
        "reloadTime":     ("float", 0.0, 9999.0, 60.0, "Ateş tekrar süresi (tick)"),
        "range":          ("float", 0.0, 9999.0, 80.0, "Menzil (px)"),
        "rotateSpeed":    ("float", 0.0,  360.0, 10.0, "Dönüş hızı (derece/tick)"),
        "inaccuracy":     ("float", 0.0,  180.0,  0.0, "Saçılım açısı (derece)"),
        "shots":          ("int",   1,    100,     1,  "Tek ateşte çıkan mermi sayısı"),
        "burstSpacing":   ("float", 0.0, 9999.0,  0.0, "Burst aralığı (tick), 0 = devre dışı"),
        "targetAir":      ("bool",  None, None,  True, "Hava birimlerini hedef alıyor mu?"),
        "targetGround":   ("bool",  None, None,  True, "Kara birimlerini hedef alıyor mu?"),
    },

    "Crafting": {
        # Üretim binalarına özgü alanlar
        "craftTime":      ("float", 0.0, 9999.0, 60.0, "Bir üretim döngüsünün süresi (tick)"),
        "itemCapacity":   ("int",   0,  99999,   10,   "Maksimum item kapasitesi"),
        "liquidCapacity": ("float", 0.0, 9999.0, 10.0, "Maksimum sıvı kapasitesi"),
        "powerConsumption":("float",0.0, 9999.0,  0.0, "Harcanan güç (birim/tick)"),
    },

    "Power": {
        # Güç üretimi/dağıtımı
        "powerProduction": ("float", 0.0, 9999.0, 0.0, "Üretilen güç (birim/tick)"),
        "powerCapacity":   ("float", 0.0, 9999.0, 0.0, "Depolanabilir güç miktarı"),
        "powerRange":      ("float", 0.0, 9999.0, 0.0, "Güç iletim menzili"),
        "conductivePower": ("bool",  None, None,  True,"Güç iletken mi?"),
    },

    "Visuals": {
        # Görsel/animasyon ayarları
        "frames":          ("int",   0, 9999,    0,   "Animasyon kare sayısı (0 = statik)"),
        "frameTime":       ("float", 0.0, 9999.0, 5.0,"Her kare süresi (tick)"),
        "teamRegion":      ("bool",  None, None, False,"Takım rengini yansıtan bölge var mı?"),
        "outlineColor":    ("str",   None, None, "",   "Dış hat rengi (hex, örn: 404049)"),
    },

    "Flags": {
        # Çeşitli boolean bayraklar
        "buildable":   ("bool", None, None,  True, "Oyuncular tarafından inşa edilebilir mi?"),
        "hidden":      ("bool", None, None, False, "Yapı editöründe gizli mi?"),
        "priority":    ("bool", None, None, False, "Düşman öncelikli hedef mi?"),
        "accessible":  ("bool", None, None,  True, "İçerik menüsünde erişilebilir mi?"),
        "sync":        ("bool", None, None,  True, "Ağda senkronize ediliyor mu?"),
    },
}

# Tüm property→kategori hızlı lookup (iç kullanım)
_PROP_TO_CATEGORY: dict[str, str] = {
    k: cat
    for cat, props in OPTIONAL_CATEGORIES.items()
    for k in props
}

# ── LİSTE GİRDİLERİ ───────────────────────────────────────────────────────
# Her biri alt alta satır eklenebilen özel alanlardır.
# ("field_key", "tip", min|None, max|None, default, "placeholder")

LIST_PROPERTIES: dict[str, dict] = {

    "researchCost": {
        "label":   "Research Cost",
        "tooltip": "Araştırmak için gereken kaynaklar (her satır bir kaynak)",
        "fields": [
            ("item",   "str", None, None, "",  "item id  (örn: copper)"),
            ("amount", "int", 0,  99999,  0,   "miktar"),
        ],
    },

    # Buraya yeni liste tipi eklemek için kopyala-yapıştır:
    # "consumes": {
    #     "label":   "Consumes",
    #     "tooltip": "Bir döngüde tüketilen kaynaklar",
    #     "fields": [
    #         ("item",   "str", None, None, "", "item id"),
    #         ("amount", "int", 0, 9999, 1,    "miktar"),
    #     ],
    # },
}


# ═════════════════════════════════════════════════════════════════════════════
#  YARDIMCI: genişletilebilir liste satır widget'ı
# ═════════════════════════════════════════════════════════════════════════════

class _ListEntryRow(QWidget):
    """Bir liste kaydını (örn: {item, amount}) temsil eden tek satır."""

    def __init__(self, fields: list[tuple], data: dict | None, on_remove, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        self._widgets: dict[str, QWidget] = {}

        for field_key, ftype, fmin, fmax, fdefault, fplaceholder in fields:
            val = (data or {}).get(field_key, fdefault)
            if ftype == "int":
                w = QSpinBox()
                w.setRange(fmin if fmin is not None else 0,
                           fmax if fmax is not None else 99999)
                w.setValue(int(val))
            elif ftype == "float":
                w = QDoubleSpinBox()
                w.setRange(fmin if fmin is not None else 0.0,
                           fmax if fmax is not None else 9999.0)
                w.setDecimals(2)
                w.setValue(float(val))
            else:
                w = QLineEdit()
                w.setPlaceholderText(fplaceholder)
                w.setText(str(val))
            w.setToolTip(fplaceholder)
            self._widgets[field_key] = w
            layout.addWidget(w)

        rm = QPushButton("✕")
        rm.setFixedSize(24, 24)
        rm.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8; color: #1e1e2e;
                border: none; border-radius: 4px;
                font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #eba0ac; }
        """)
        rm.clicked.connect(on_remove)
        layout.addWidget(rm)

    def get_data(self) -> dict:
        result = {}
        for k, w in self._widgets.items():
            if isinstance(w, QCheckBox):
                result[k] = w.isChecked()
            elif isinstance(w, QSpinBox):
                result[k] = w.value()
            elif isinstance(w, QDoubleSpinBox):
                result[k] = w.value()
            else:
                result[k] = w.text().strip()
        return result


class _ListPropertyWidget(QWidget):
    """
    Başlık + '+' butonu + satır listesi.
    Tek bir LIST_PROPERTIES girişinin tüm UI'ı.
    """

    def __init__(self, key: str, spec: dict, existing: list | None, parent=None):
        super().__init__(parent)
        self._key    = key
        self._spec   = spec
        self._rows: list[_ListEntryRow] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # Başlık satırı
        header = QHBoxLayout()
        lbl = QLabel(spec["label"])
        lbl.setStyleSheet("color: #89b4fa; font-size: 12px; font-weight: bold;")
        if spec.get("tooltip"):
            lbl.setToolTip(spec["tooltip"])
        add_btn = QPushButton("+ Satır Ekle")
        add_btn.setFixedHeight(22)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244; color: #cdd6f4;
                border: none; border-radius: 4px;
                padding: 2px 8px; font-size: 12px;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        add_btn.clicked.connect(self._add_row)
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(add_btn)
        outer.addLayout(header)

        # Alan adı ipuçları (küçük gri)
        hints = "  |  ".join(f[0] for f in spec["fields"])
        hint_lbl = QLabel(hints)
        hint_lbl.setStyleSheet("color: #585b70; font-size: 10px;")
        outer.addWidget(hint_lbl)

        # Satır konteyner
        self._rows_container = QVBoxLayout()
        self._rows_container.setSpacing(2)
        outer.addLayout(self._rows_container)

        # Mevcut veriyi yükle
        for entry in (existing or []):
            self._add_row(entry)

    def _add_row(self, data: dict | None = None):
        row = _ListEntryRow(
            self._spec["fields"], data,
            on_remove=lambda: self._remove_row(row),
        )
        self._rows.append(row)
        self._rows_container.addWidget(row)

    def _remove_row(self, row: _ListEntryRow):
        if row in self._rows:
            self._rows.remove(row)
            row.setParent(None)
            row.deleteLater()

    def get_value(self) -> list[dict]:
        return [r.get_data() for r in self._rows]


# ═════════════════════════════════════════════════════════════════════════════
#  ANA EDITOR
# ═════════════════════════════════════════════════════════════════════════════

class BlockEditor(QWidget):
    def __init__(self, content: dict, project, parent=None):
        super().__init__(parent)
        self.content     = content
        self.project     = project
        self.sprite_path = content.get("sprite", "")
        self.main_window = None

        # Aktif opsiyonel skalar alanlar: key → widget
        self.active_props: dict[str, QWidget] = {}

        # Aktif liste alanlar: key → _ListPropertyWidget
        self.active_lists: dict[str, _ListPropertyWidget] = {}

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
            QMenu::separator { height: 1px; background: #313244; margin: 2px 0; }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SOL PANEL ─────────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_layout.setSpacing(12)

        title = QLabel("Block Editor")
        title.setStyleSheet("color: #89b4fa; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.form_container = QWidget()
        self.form_main = QVBoxLayout(self.form_container)
        self.form_main.setContentsMargins(0, 0, 0, 0)
        self.form_main.setSpacing(0)

        # Zorunlu alanlar
        basic_w = QWidget()
        self.basic_form = QFormLayout(basic_w)
        self.basic_form.setSpacing(10)
        self.basic_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input         = self._make_input("my-block")
        self.display_name_input = self._make_input("My Block")

        self.basic_form.addRow(self._lbl("name",        "Blok ID (kod içinde kullanılır, boşluk yok)"),     self.name_input)
        self.basic_form.addRow(self._lbl("displayName", "Oyun içinde gösterilecek isim"),  self.display_name_input)

        self.form_main.addWidget(basic_w)

        # ── Opsiyonel alanlar bölümü ──
        sep = QLabel("── Optional Properties ──")
        sep.setStyleSheet("color: #585b70; font-size: 11px; padding-top: 14px; padding-bottom: 4px;")
        self.form_main.addWidget(sep)

        # Skalar opsiyonel alanların form'u
        self.opt_w = QWidget()
        self.opt_form = QFormLayout(self.opt_w)
        self.opt_form.setSpacing(10)
        self.opt_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_main.addWidget(self.opt_w)

        # Liste alanlarının konteynerı
        self.lists_container = QVBoxLayout()
        self.lists_container.setSpacing(12)
        self.form_main.addLayout(self.lists_container)

        # Add Property butonu
        self.add_prop_btn = QPushButton("+ Add Property")
        self.add_prop_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244; color: #cdd6f4;
                border: none; border-radius: 4px;
                padding: 6px 12px; font-size: 13px; text-align: left;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.add_prop_btn.clicked.connect(self._open_add_menu)
        self.form_main.addWidget(self.add_prop_btn)
        self.form_main.addStretch()

        scroll.setWidget(self.form_container)
        left_layout.addWidget(scroll)

        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #89b4fa; color: #1e1e2e; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #74c7ec; }
        """)
        save_btn.clicked.connect(self._save)
        left_layout.addWidget(save_btn)

        # ── SAĞ PANEL (sprite) ─────────────────────────────────────
        right = QWidget()
        right.setFixedWidth(240)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_layout.addWidget(QLabel("Sprite"))

        self.sprite_preview = QLabel()
        self.sprite_preview.setFixedSize(180, 180)
        self.sprite_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_preview.setStyleSheet("""
            background-color: #1e1e2e; border: 1px solid #313244;
            border-radius: 8px; color: #585b70; font-size: 13px;
        """)
        self.sprite_preview.setText("No sprite")

        sprite_btn = QPushButton("Load Sprite")
        sprite_btn.setStyleSheet("""
            QPushButton { background-color: #313244; color: #cdd6f4; border: none; border-radius: 4px; padding: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #45475a; }
        """)
        sprite_btn.clicked.connect(self._load_sprite)

        right_layout.addWidget(self.sprite_preview)
        right_layout.addWidget(sprite_btn)

        root.addWidget(left, stretch=1)
        root.addWidget(right)

        self._populate()

    # ── YARDIMCI ──────────────────────────────────────────────────

    def _lbl(self, key: str, tooltip: str = "") -> QLabel:
        # OPTIONAL_CATEGORIES içindeyse oradaki tooltip'i kullan
        for cat, props in OPTIONAL_CATEGORIES.items():
            if key in props:
                tooltip = props[key][4] if len(props[key]) > 4 else tooltip
                break
        label = QLabel(f"{key}:")
        label.setStyleSheet("color: #cdd6f4; font-size: 13px; background: transparent;")
        if tooltip:
            label.setToolTip(tooltip)
        return label

    def _make_input(self, placeholder="") -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        return w

    def _make_scalar_widget(self, key: str) -> QWidget:
        ptype, mn, mx, default, *_ = OPTIONAL_CATEGORIES[_PROP_TO_CATEGORY[key]][key]
        if ptype == "int":
            w = QSpinBox(); w.setRange(mn, mx); w.setValue(self.content.get(key, default))
        elif ptype == "float":
            w = QDoubleSpinBox(); w.setRange(mn, mx); w.setDecimals(2); w.setValue(self.content.get(key, default))
        elif ptype == "bool":
            w = QCheckBox(); w.setChecked(self.content.get(key, default))
        else:
            w = QLineEdit(); w.setText(str(self.content.get(key, default)))
        return w

    # ── ADD PROPERTY MENÜSÜ ───────────────────────────────────────

    def _open_add_menu(self):
        menu = QMenu(self)

        # Kategorilere ayrılmış skalar property'ler
        any_scalar = False
        for cat, props in OPTIONAL_CATEGORIES.items():
            available = [k for k in props if k not in self.active_props]
            if not available:
                continue
            any_scalar = True
            cat_menu = menu.addMenu(f"▸ {cat}")
            for key in available:
                a = cat_menu.addAction(key)
                a.setData(("scalar", key))

        # Liste property'leri (tek düzey, ayrı başlık altında)
        available_lists = [k for k in LIST_PROPERTIES if k not in self.active_lists]
        if available_lists:
            if any_scalar:
                menu.addSeparator()
            list_menu = menu.addMenu("▸ List Properties")
            for key in available_lists:
                spec = LIST_PROPERTIES[key]
                a = list_menu.addAction(spec["label"])
                a.setData(("list", key))

        if not any_scalar and not available_lists:
            menu.addAction("Tüm property'ler eklendi").setEnabled(False)

        chosen = menu.exec(self.add_prop_btn.mapToGlobal(
            self.add_prop_btn.rect().bottomLeft()
        ))
        if chosen and chosen.data():
            kind, key = chosen.data()
            if kind == "scalar":
                self._add_scalar_prop(key)
            else:
                self._add_list_prop(key)

    # ── SKALAR PROP EKLE/KALDIR ───────────────────────────────────

    def _add_scalar_prop(self, key: str):
        if key in self.active_props:
            return
        widget = self._make_scalar_widget(key)

        row_w = QWidget()
        row_l = QHBoxLayout(row_w)
        row_l.setContentsMargins(0, 0, 0, 0)
        row_l.setSpacing(4)
        row_l.addWidget(widget, stretch=1)

        rm = QPushButton("✕")
        rm.setFixedSize(24, 24)
        rm.setStyleSheet("""
            QPushButton { background-color: #f38ba8; color: #1e1e2e; border: none; border-radius: 4px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: #eba0ac; }
        """)
        rm.clicked.connect(lambda: self._remove_scalar_prop(key))
        row_l.addWidget(rm)

        self.opt_form.addRow(self._lbl(key), row_w)
        self.active_props[key] = widget

    def _remove_scalar_prop(self, key: str):
        if key not in self.active_props:
            return
        widget = self.active_props.pop(key)
        for i in range(self.opt_form.rowCount()):
            item = self.opt_form.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if item and item.widget():
                row_w = item.widget()
                lo = row_w.layout()
                if lo and lo.count() > 0 and lo.itemAt(0).widget() is widget:
                    self.opt_form.removeRow(i)
                    break
        self.content.pop(key, None)

    # ── LİSTE PROP EKLE/KALDIR ────────────────────────────────────

    def _add_list_prop(self, key: str, existing: list | None = None):
        if key in self.active_lists:
            return
        spec   = LIST_PROPERTIES[key]
        lw     = _ListPropertyWidget(key, spec, existing)

        # Üst çizgi ayracı
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")

        # Kaldır butonu satırı
        rm_btn = QPushButton(f"✕  {spec['label']} kaldır")
        rm_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #f38ba8; border: none; font-size: 11px; text-align: left; padding: 0; }
            QPushButton:hover { color: #eba0ac; }
        """)
        rm_btn.clicked.connect(lambda: self._remove_list_prop(key, sep, lw, rm_btn))

        self.lists_container.addWidget(sep)
        self.lists_container.addWidget(lw)
        self.lists_container.addWidget(rm_btn)
        self.active_lists[key] = lw

    def _remove_list_prop(self, key: str, sep: QFrame,
                          lw: _ListPropertyWidget, rm_btn: QPushButton):
        self.active_lists.pop(key, None)
        self.content.pop(key, None)
        for w in (sep, lw, rm_btn):
            w.setParent(None)
            w.deleteLater()

    # ── VERİ ──────────────────────────────────────────────────────

    def _populate(self):
        self.name_input.setText(self.content.get("name", ""))
        self.display_name_input.setText(self.content.get("displayName", ""))

        # Mevcut skalar opsiyonel alanları yükle
        for cat, props in OPTIONAL_CATEGORIES.items():
            for key in props:
                if key in self.content:
                    self._add_scalar_prop(key)

        # Mevcut liste alanları yükle
        for key, spec in LIST_PROPERTIES.items():
            if key in self.content:
                self._add_list_prop(key, existing=self.content[key])

        if self.sprite_path:
            self._update_sprite_preview(self.sprite_path)

    def _load_sprite(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Sprite", "", "Images (*.png)")
        if path:
            import shutil
            sprites_dir = os.path.join(self.project.path, "sprites")
            os.makedirs(sprites_dir, exist_ok=True)
            dest = os.path.join(sprites_dir, os.path.basename(path))
            if os.path.abspath(path) != os.path.abspath(dest):
                shutil.copy2(path, dest)
            self.sprite_path = dest
            self._update_sprite_preview(dest)

    def _update_sprite_preview(self, path: str):
        px = QPixmap(path)
        if not px.isNull():
            self.sprite_preview.setPixmap(
                px.scaled(170, 170,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
            )
            self.sprite_preview.setText("")

    def _get_scalar_value(self, key: str):
        w = self.active_props[key]
        if isinstance(w, QCheckBox):    return w.isChecked()
        if isinstance(w, QSpinBox):     return w.value()
        if isinstance(w, QDoubleSpinBox): return w.value()
        return w.text().strip()

    # ── KAYDET ────────────────────────────────────────────────────

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Hata", "Name (ID) boş olamaz.")
            return

        self.content["type"]        = "block"
        self.content["name"]        = name
        self.content["displayName"] = self.display_name_input.text().strip()
        self.content["sprite"]      = self.sprite_path

        # Skalar opsiyonel
        for key in list(self.active_props.keys()):
            self.content[key] = self._get_scalar_value(key)

        # Liste opsiyonel
        for key, lw in self.active_lists.items():
            self.content[key] = lw.get_value()

        # Projeye kaydet
        found = any(c is self.content for c in self.project.contents)
        if found:
            idx = next(i for i, c in enumerate(self.project.contents) if c is self.content)
            self.project.contents[idx] = self.content
        else:
            self.project.contents.append(self.content)
        self.project.save()

        # HJSON yaz
        blocks_dir = os.path.join(self.project.path, "content", "blocks")
        os.makedirs(blocks_dir, exist_ok=True)

        hjson_data: dict = {
            "type": "block",
            "name": self.content["name"],
        }

        # Skalar opsiyonel alanlar
        for key in self.active_props:
            hjson_data[key] = self.content[key]

        # Liste alanlar
        for key in self.active_lists:
            hjson_data[key] = self.content[key]

        hjson_path = os.path.join(blocks_dir, f"{name}.hjson")
        with open(hjson_path, "w", encoding="utf-8") as f:
            hjson.dump(hjson_data, f, ensure_ascii=False, indent=2)

        if self.main_window and hasattr(self.main_window, "grid_view"):
            self.main_window.grid_view.refresh()
        if self.main_window and hasattr(self.main_window, "editor_window"):
            self.main_window.editor_window.setWindowTitle(
                f"Block Editor — {name}"
            )
