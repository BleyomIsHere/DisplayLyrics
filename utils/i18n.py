import json
import os

class Translator:
    def __init__(self, lang_code="en", lang_dir="lang"):
        self.lang_code = lang_code
        self.lang_dir = lang_dir
        self.translations = self.load_translations()

    def load_translations(self):
        try:
            path = os.path.join(self.lang_dir, f"{self.lang_code}.json")
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[I18N] Error loading '{self.lang_code}.json': {e}")
            if self.lang_code != "en":
                try:
                    with open(os.path.join(self.lang_dir, "en.json"), 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return {}
            return {}

    def t(self, key):
        return self.translations.get(key, key)

    def tf(self, key, **kwargs):
        text = self.t(key)
        try:
            return text.format(**kwargs)
        except Exception as e:
            print(f"[I18N] Error formatting key '{key}': {e}")
            return text

