# ECVAMM — Yayın Öncesi Sorunlar ve Yapılacaklar

## 🔴 Critical — Yayın Öncesi Çözülmeli

### 1. grid_view.py:141-144 — Silme hatası (type_to_dir eksik)
`ContentCard._delete_file()` içindeki `type_to_dir` sözlüğünde `"block"`, `"turret"`, `"conveyor"`, `"crafter"` eksik.
Turret/crafter silerken HJSON dosyası `content/turrets/` yerine `content/turrets/` altında (fallback `ctype + "s"`) aranıyor, doğru klasör `content/blocks/` olduğu için dosya bulunamıyor ve **silme sessizce başarısız oluyor**.
- **Çözüm**: `TYPE_TO_DIR` tek bir modülde tanımlanıp (`core/constants.py` gibi) her yerden import edilmeli.

### 2. bottom_bar.py:42-44 — `update()` metodu QWidget.update()'i eziyor
`def update()` → `QWidget.update()` Qt'in paint-event mekanizmasını bozar.
- **Çözüm**: `refresh()` veya `update_project_info()` olarak yeniden adlandırılmalı, tüm çağrılar güncellenmeli.

---

## 🟡 High — Yayın Öncesi Çözülmeli

### 3. base_block_editor.py:183,185,186 — Türkçe hardcoded string'ler
`researchCost` list property'sinde:
- Tooltip: `"Araştırmak için gereken kaynaklar (her satır bir kaynak)"`
- Placeholder: `"item id  (örn: copper)"` — "örn" Türkçe
- Placeholder: `"miktar"` — Türkçe
Bunlar locale üzerinden çevrilmeli.

### 4. project.py:245-248 — create_new_project versiyon dialog girdilerini yok sayıyor
`create_new_project()` fonksiyonu `mod_info` dict'inden `version` ve `minGameVersion` anahtarlarını okumuyor.
Kullanıcının `NewModDialog`'da girdiği versiyon ve min oyun versiyonu kaydedilmiyor, her zaman varsayılan (`"1.0"`, `"145"`) yazılıyor.

### 5. base_block_editor.py:175 — requirements placeholder'ları locale kullanmıyor
`block_editor.placeholder_item` ve `block_editor.placeholder_amount` locale anahtarları tanımlı ama kod hala hardcoded `"item name (e.g. copper)"` ve `"amount"` kullanıyor.

---

## 🟢 Medium — Önerilen

### 6. TYPE_TO_DIR 3 dosyada parçalanmış
- `base_block_editor.py:204-214` — 9 giriş
- `grid_view.py:141-144` — 6 giriş (eksik: block, turret, conveyor, crafter)
- `project.py:156-163` — 6 giriş (aynı eksik)
Tek bir kaynağa çekilmeli (`core/constants.py`).

### 7. MINDUSTRY_ITEMS tekrarı
`item_editor.py:17-23` ve `base_block_editor.py:74-80`'de aynı liste tekrarlanmış. Tek kaynağa çekilmeli.

### 8. Kullanılmayan import'lar
- `base_block_editor.py`: `QStringListModel` (line 67), `QAction` (line 68)
- `item_editor.py`: `QApplication` (line 7), `QStringListModel` (line 10), `QAction` (line 11)

### 9. config.json hataları
- `"font_family": "cabiri"` yazım hatası (muhtemelen "Calibri" olmalı)
- `default_author`, `default_desc`, `default_version`, `default_min_version` eksik (ilk kayıtta ekleniyor, ama başlangıçta yok)

### 10. GitHub linki placeholder
`main_window.py:159` — `https://github.com/USERNAME/REPO` gerçek linkle değiştirilmeli.

### 11. credits.text bozuk İngilizce
`locale/langs/en.json:62` — `"I did here for other updates."` anlamsız.
`locale/langs/tr.json:62` — Aynı İngilizce metin Türkçe'ye çevrilmemiş.

### 12. settings ayarlar btn tooltip'i eksik
`main_window.py:180` — `btn_new` ve `btn_open` tooltip'i var ama `btn_setting`'in tooltip'i yok.

---

## 🔵 Low — Düzeltilebilir

### 13. Ölü locale anahtarları
- `dialog.settings_not_ready` — Hiçbir yerde kullanılmıyor
- `dialog.build_not_ready` — Hiçbir yerde kullanılmıyor
- `select.sprite` — Hiçbir yerde kullanılmıyor (kodda `"Select Sprite"` hardcoded)
- `settings.restart_notice` — Tanımlı ama kodda gösterilmiyor
- `tooltip.item.details` — `details` property'si `OPTIONAL_PROPERTIES`'te yok

### 14. item_editor.py:436 — `research` pop() fragile
`self.content.pop("research", None)` ile research geçici olarak çıkarılıyor, sonra geri ekleniyor.
Arada exception olursa `self.content`'ten kalıcı olarak kaybolur. try/finally ile korunmalı.

### 15. Hardcoded "Select Sprite"
`base_block_editor.py:744` ve `item_editor.py:382`'de `tr("select.sprite")` yerine `"Select Sprite"` kullanılmış.

### 16. settings.py:309 — Versiyon hardcoded
`"Version: 0.1.0"` sabit kodlanmış. Tek bir sabit (`__version__`) tanımlanmalı.

### 17. waypoint_dialog.py:85-86 — datetime import döngü içinde
`from datetime import datetime` her yinelemede çalışıyor. Dosya başına taşınmalı.

### 18. main.py:25-33 ve main_window.py:182-189 — QToolTip stylesheet tekrarı
Aynı stylesheet iki kere uygulanıyor (QApplication + QMainWindow). Biri yeterli.

### 19. project.py:XOR_KEY eski proje adı
`_XOR_KEY = b"mindcreator_key_2024"` — "mindcreator" hâlâ duruyor.

### 20. LISCENSE → LICENSE yazım hatası
Dosya adı `LISCENSE` yerine `LICENSE` olmalı.

### 21. Boş dosyalar
- `updater.py` — tamamen boş
- `bundle/bundle_manager.py` — tamamen boş
- `bundle/languages.py` — tamamen boş

---

## Plan

| # | Dosya(lar) | Değişiklik | Öncelik |
|---|-----------|-----------|---------|
| 1 | `grid_view.py`, `core/constants.py` (yeni) | TYPE_TO_DIR tek kaynak, grid_view düzelt | 🔴 |
| 2 | `bottom_bar.py`, tüm çağrılar | `update()` → `refresh()` | 🔴 |
| 3 | `base_block_editor.py`, locale | researchCost string'leri locale'e taşı | 🟡 |
| 4 | `project.py` | create_new_project version/minGameVersion oku | 🟡 |
| 5 | `base_block_editor.py` | requirements placeholder locale kullan | 🟡 |
| 6 | `core/constants.py` | TYPE_TO_DIR, MINDUSTRY_ITEMS tek kaynak | 🟢 |
| 7 | `base_block_editor.py`, `item_editor.py` | MINDUSTRY_ITEMS import | 🟢 |
| 8 | Her iki editor | Kullanılmayan importları temizle | 🟢 |
| 9 | `config.json` | font_family düzelt, default keys ekle | 🟢 |
| 10 | `main_window.py` | GitHub linki güncelle | 🟢 |
| 11 | `locale/langs/*.json` | credits.text düzelt | 🟢 |
| 12 | `main_window.py` | btn_setting tooltip ekle | 🟢 |
