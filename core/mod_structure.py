# core/mod_structure.py
import os
import hjson

CONTENT_DIRS = [
    "content/items",
    "content/blocks",
    "content/liquids",
    "content/units",
    "maps",
    "bundles",
    "sounds",
    "schematics",
    "scripts",
    "sprites-override",
    "sprites",
]

DEFAULT_MOD_HJSON = {
    "name": "",
    "displayName": "",
    "author": "",
    "description": "",
    "version": "1.0",
    "minGameVersion": "157.4",
    "dependencies": [],
    "hidden": False,
}

def create_mod_structure(base_path: str, mod_info: dict) -> bool:
    """
    base_path: Kullanıcının seçtiği klasör
    mod_info: name, displayName, author, description
    """
    try:
        # Klasörleri oluştur
        for dir_path in CONTENT_DIRS:
            os.makedirs(os.path.join(base_path, dir_path), exist_ok=True)

        # mod.hjson oluştur
        mod_data = DEFAULT_MOD_HJSON.copy()
        mod_data.update(mod_info)

        mod_hjson_path = os.path.join(base_path, "mod.hjson")
        with open(mod_hjson_path, "w", encoding="utf-8") as f:
            hjson.dump(mod_data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"Mod yapısı oluşturulamadı: {e}")
        return False


def is_valid_mod(base_path: str) -> bool:
    """Klasörün geçerli bir MindCreator modu olup olmadığını kontrol eder."""
    mindtool_path = os.path.join(base_path, ".mindtool.json")
    mod_hjson_path = os.path.join(base_path, "mod.hjson")
    return os.path.exists(mindtool_path) and os.path.exists(mod_hjson_path)
