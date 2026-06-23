# config/static/main.py
from config.settings import BASE_DIR, DEBUG
from config.apps import APPS_DIR



STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # Необходимо для работы compressor
    'sass_processor.finders.CssFinder',  # Для поиска SCSS файлов
]


MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_DIRS = [
    BASE_DIR / 'apps' / 'static',
]
STATIC_ROOT = BASE_DIR / 'static'