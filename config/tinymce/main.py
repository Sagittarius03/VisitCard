# tinymce/main.py
from config.settings import DEBUG
from .default import TINYMCE_DEFAULT_CONFIG

TINYMCE_CONFIG = TINYMCE_DEFAULT_CONFIG

# Остальные настройки остаются
TINYMCE_JS_URL = '/static/tinymce/tinymce.min.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False