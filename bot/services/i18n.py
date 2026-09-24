import json
import os
from typing import Dict


class I18n:
    def __init__(self, locales_dir: str):
        self.locales_dir = locales_dir
        self.locales: Dict[str, Dict[str, str]] = {}
        self.load_locales()

    def load_locales(self):
        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                lang = filename.split(".")[0]
                filepath = os.path.join(self.locales_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    self.locales[lang] = json.load(f)

    def get(self, key: str, lang: str = "en", **kwargs) -> str:
        if lang not in self.locales:
            lang = "en"

        text = self.locales.get(lang, {}).get(key, key)

        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text


# Initialize a global instance
i18n = I18n(
    os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)),
        "locales"))


def _(key: str, lang: str = "en", **kwargs) -> str:
    return i18n.get(key, lang, **kwargs)
