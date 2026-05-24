# locale/locale_manager.py
import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def _read_config() -> dict:
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_config(config: dict):
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class LocaleManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._strings = {}
            cls._instance._current_lang = "en"
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config = _read_config()
        self._current_lang = config.get("language", "en")
        self._load_lang()

    def set_language(self, lang: str):
        self._current_lang = lang
        self._load_lang()
        config = _read_config()
        config["language"] = lang
        _write_config(config)

    def get_language(self) -> str:
        return self._current_lang

    def get(self, key: str, default: str = "") -> str:
        return self._strings.get(key, default or key)

    def _load_lang(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "locale", "langs", f"{self._current_lang}.json"
        )
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._strings = json.load(f)
        except Exception:
            self._strings = {}

    def available_languages(self) -> list[tuple[str, str]]:
        langs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale", "langs")
        result = []
        try:
            for fname in sorted(os.listdir(langs_dir)):
                if fname.endswith(".json"):
                    code = fname[:-5]
                    try:
                        with open(os.path.join(langs_dir, fname), "r", encoding="utf-8") as f:
                            data = json.load(f)
                        name = data.get("_lang_name", code)
                    except Exception:
                        name = code
                    result.append((code, name))
        except Exception:
            pass
        return result


def tr(key: str, default: str = "") -> str:
    return LocaleManager().get(key, default)
