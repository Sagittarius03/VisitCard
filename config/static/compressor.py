# config/static/compressor.py
from config.settings import *

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False  # Для разработки оставляем False
COMPRESS_DEBUG_TOGGLE = 'compress'

# Указываем, что используем Jinja2
COMPRESS_JINJA2_GET_ENVIRONMENT = 'config.jinja2.env.environment'

# Расширения файлов для обработки
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',  # Для минификации CSS
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',  # Для минификации JS
]

# Настройки для разработки
if DEBUG:
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = False
else:
    COMPRESS_OFFLINE = True
    COMPRESS_OFFLINE_CONTEXT = {}