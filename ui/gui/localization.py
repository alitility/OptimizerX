import gettext
import os

# locales dizini: ui/gui/locales/
BASEDIR = os.path.dirname(__file__)
LOCALEDIR = os.path.join(BASEDIR, "locales")

# Global çeviri fonksiyonu, başlangıçta TR
_ = lambda s: s

def set_language(lang_code: str):
    global _
    try:
        t = gettext.translation(
            "optimizerx", LOCALEDIR,
            languages=[lang_code], fallback=True
        )
        _ = t.gettext
    except Exception:
        _ = lambda s: s