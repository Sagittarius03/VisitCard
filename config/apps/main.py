from .utils import *

DJANGO_CORE_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', 
]

# Сторонние приложения
THIRD_PARTY_APPS = [
    'django_jinja2',        # Jinja2 шаблонизатор для Django
    'compressor',          # Сжатие файлов
    'sass_processor',      # Для компиляции SCSS/Sass в CSS 
    'tinymce',             # WYSIWYG редактор
    'django_ace',          # Редактор контента с подсветкой синтаксиса
    # 'django_bootstrap5',
    'django.contrib.sitemaps', #Карта сайта
    
    'django_extensions',
    'easy_thumbnails',
    'filer',
    'mptt',
]

# Использование функций
try:
    # Автоматически находим приложения
    AUTO_APPS = get_installed_apps()
    
    # AUTO_APPS, APP_CONFIGS = get_apps_with_config()  
except Exception as e:
    print(f"❌ Ошибка при поиске приложений: {e}")
    AUTO_APPS = []
    

CUSTOM_APPS = AUTO_APPS

INSTALLED_APPS = CUSTOM_APPS + DJANGO_CORE_APPS + THIRD_PARTY_APPS
