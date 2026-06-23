# cache.py
from .settings import BASE_DIR, DEBUG
# Настройки кэширования
if DEBUG:
    # Полностью отключаем кэш в разработке
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # Фиктивный кэш
        },
        'memory': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }
    CACHE_MIDDLEWARE_SECONDS = 0
    CACHE_MIDDLEWARE_ALIAS = 'default'
else:
    # Продакшен настройки
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': BASE_DIR / 'cache' / 'default',
            'TIMEOUT': 60 * 60 * 24,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        },
        'memory': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 60 * 5,
            'OPTIONS': {
                'MAX_ENTRIES': 100,
            }
        },
    }
    CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 2
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_KEY_PREFIX = 'legion21'