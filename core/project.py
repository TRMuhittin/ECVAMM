# core/project.py
import os
import json
import base64
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
        self.version: str = "1.0"
        self.min_game_version: str = "157.4"
        self.contents = data.get("contents", [])

    def save(self) -> bool:
        """Projeyi .mindtool.json olarak kaydeder."""
        try:
            mindtool_path = os.path.join(self.path, ".mindtool.json")
            encoded = _encode(self.to_dict())
            with open(mindtool_path, "w", encoding="utf-8") as f:
                f.write(encoded)
            return True
        except Exception as e:
            print(f"Proje kaydedilemedi: {e}")
            return False

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
