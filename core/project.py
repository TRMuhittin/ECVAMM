# core/project.py
import os
import json
import base64
from datetime import datetime
from core.mod_structure import create_mod_structure, is_valid_mod

# Basit XOR şifreleme için sabit key
_XOR_KEY = b"mindcreator_key_2024"

def _xor(data: bytes) -> bytes:
    key = _XOR_KEY
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def _encode(data: dict) -> str:
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(_xor(raw)).decode("utf-8")

def _decode(encoded: str) -> dict:
    raw = _xor(base64.b64decode(encoded.encode("utf-8")))
    return json.loads(raw.decode("utf-8"))


class Project:
    def __init__(self):
        self.path: str = ""
        self.name: str = ""
        self.display_name: str = ""
        self.author: str = ""
        self.description: str = ""
        self.version: str = "1.0"
        self.min_game_version: str = "145"
        self.contents: list = []  # Grid'deki tüm içerikler

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "displayName": self.display_name,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "minGameVersion": self.min_game_version,
            "contents": self.contents,
        }

    def from_dict(self, data: dict):
        self.name = data.get("name", "")
        self.display_name = data.get("displayName", "")
        self.author = data.get("author", "")
        self.description = data.get("description", "")
        self.version = data.get("version", "1.0")
        self.min_game_version = str(data.get("minGameVersion", "157.4"))
        self.contents = data.get("contents", [])

    def save(self) -> bool:
        """Projeyi .mindtool.json olarak kaydeder. Ayarlarda açıksa waypoint de oluşturur."""
        try:
            mindtool_path = os.path.join(self.path, ".mindtool.json")
            encoded = _encode(self.to_dict())
            with open(mindtool_path, "w", encoding="utf-8") as f:
                f.write(encoded)
            _cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
            try:
                with open(_cfg_path, "r") as f:
                    cfg = json.load(f)
                if cfg.get("editor_auto_save", False):
                    self.save_waypoint()
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"Proje kaydedilemedi: {e}")
            return False

    # ── Waypoint / Snapshot ────────────────────────────────────────

    def _waypoint_path(self, timestamp: str = "") -> str:
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.path, f".mindtool-{timestamp}.json")

    def save_waypoint(self) -> str | None:
        """Zaman damgalı bir kopya oluşturur. Dosya adını döndürür."""
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            wp_path = self._waypoint_path(ts)
            encoded = _encode(self.to_dict())
            with open(wp_path, "w", encoding="utf-8") as f:
                f.write(encoded)
            return ts
        except Exception as e:
            print(f"Waypoint kaydedilemedi: {e}")
            return None

    @staticmethod
    def list_waypoints(path: str) -> list[dict]:
        """Proje klasöründeki waypoint'leri listeler (timestamp sıralı)."""
        waypoints = []
        try:
            for fname in os.listdir(path):
                if fname.startswith(".mindtool-") and fname.endswith(".json"):
                    ts = fname[len(".mindtool-"):-len(".json")]
                    full = os.path.join(path, fname)
                    mtime = os.path.getmtime(full)
                    waypoints.append({"ts": ts, "path": full, "mtime": mtime})
        except Exception:
            pass
        waypoints.sort(key=lambda w: w["mtime"], reverse=True)
        return waypoints

    @staticmethod
    def load_waypoint(path: str, ts: str) -> "Project | None":
        """Belirli bir waypoint'ten proje yükler."""
        try:
            wp_path = os.path.join(path, f".mindtool-{ts}.json")
            if not os.path.exists(wp_path):
                return None
            with open(wp_path, "r", encoding="utf-8") as f:
                encoded = f.read()
            data = _decode(encoded)
            project = Project()
            project.path = path
            project.from_dict(data)
            return project
        except Exception as e:
            print(f"Waypoint yüklenemedi: {e}")
            return None

    @staticmethod
    def clean_waypoints(path: str, keep: int = 10):
        """En son `keep` adet waypoint dışındakileri siler."""
        wps = Project.list_waypoints(path)
        for wp in wps[keep:]:
            try:
                os.remove(wp["path"])
            except Exception:
                pass

    def load(self, path: str) -> bool:
        try:
            if not is_valid_mod(path):
                return False
            self.path = path
            mindtool_path = os.path.join(path, ".mindtool.json")
            with open(mindtool_path, "r", encoding="utf-8") as f:
                encoded = f.read()
            data = _decode(encoded)
            self.from_dict(data)

        # HJSON dosyası olmayan içerikleri temizle
            import hjson
            valid_contents = []
            for c in self.contents:
                ctype = c.get("type", "")
                cname = c.get("name", "")
                type_to_dir = {
                    "item": "items",
                    "floor": "blocks",
                    "wall": "blocks",
                    "turret": "blocks",
                    "unit": "units",
                    "liquid": "liquids",
                }
                folder = type_to_dir.get(ctype, ctype + "s")
                hjson_path = os.path.join(path, "content", folder, f"{cname}.hjson")
                if os.path.exists(hjson_path):
                    valid_contents.append(c)

            self.contents = valid_contents
            self.save()  # Temizlenmiş hali kaydet
            return True

        except Exception as e:
            print(f"Proje yüklenemedi: {e}")
            return False


def recover_project(path: str) -> Project | None:
    """
    mod.hjson + content/*.hjson dosyalarından projeyi kurtarır.
    .mindtool.json olmayan veya bozulmuş projeler için kullanılır.
    """
    try:
        mod_hjson_path = os.path.join(path, "mod.hjson")
        mod_hjson_path_exists = os.path.exists(mod_hjson_path)
        if not mod_hjson_path_exists:
            return None

        import hjson
        with open(mod_hjson_path, "r", encoding="utf-8") as f:
            mod_data = hjson.load(f)

        project = Project()
        project.path = path
        project.name = mod_data.get("name", "")
        project.display_name = mod_data.get("displayName", "")
        project.author = mod_data.get("author", "")
        project.description = mod_data.get("description", "")
        project.version = mod_data.get("version", "1.0")
        project.min_game_version = str(mod_data.get("minGameVersion", "157.4"))

        # İçerik dizinlerini tara
        scan_dirs = {
            "items":   "item",
            "blocks":  None,   # HJSON içinden type okunacak
            "units":   "unit",
            "liquids": "liquid",
        }
        for subdir, default_type in scan_dirs.items():
            content_dir = os.path.join(path, "content", subdir)
            if not os.path.isdir(content_dir):
                continue
            for fname in sorted(os.listdir(content_dir)):
                if not fname.endswith(".hjson"):
                    continue
                hjson_path = os.path.join(content_dir, fname)
                try:
                    with open(hjson_path, "r", encoding="utf-8") as f:
                        data = hjson.load(f)
                except Exception:
                    continue
                name = data.get("name", fname[:-5])
                ctype = data.get("type", default_type or "block")
                sprite_dir = os.path.join(path, "sprites", subdir)
                sprite = ""
                for ext in (".png", ".jpg", ".jpeg"):
                    sp = os.path.join(sprite_dir, f"{name}{ext}")
                    if os.path.exists(sp):
                        sprite = sp
                        break
                entry = {"type": ctype, "name": name, "sprite": sprite}
                for key in ("displayName", "description", "color"):
                    if key in data:
                        entry[key] = data[key]
                project.contents.append(entry)

        project.save()
        return project

    except Exception as e:
        print(f"Proje kurtarılamadı: {e}")
        return None


def create_new_project(base_path: str, mod_info: dict) -> Project | None:
    """
    Yeni proje oluşturur, klasör yapısını kurar, .mindtool.json yazar.
    mod_info: name, displayName, author, description
    """
    try:
        # Mod klasörü
        mod_path = os.path.join(base_path, mod_info["name"])
        os.makedirs(mod_path, exist_ok=True)

        # Klasör yapısını oluştur
        if not create_mod_structure(mod_path, mod_info):
            return None

        # Proje objesi
        project = Project()
        project.path = mod_path
        project.name = mod_info.get("name", "")
        project.display_name = mod_info.get("displayName", "")
        project.author = mod_info.get("author", "")
        project.description = mod_info.get("description", "")

        # .mindtool.json kaydet
        if not project.save():
            return None

        return project

    except Exception as e:
        print(f"Proje oluşturulamadı: {e}")
        return None
