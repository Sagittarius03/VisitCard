import sys
from pathlib import Path
from datetime import datetime
from utils.text_format import printf, STYLES, printf_table

from .settings import *
from .cache import *
from .static.main import *
from .static.sass import *
from .middleware import *
from .jinja2 import *
from .apps import *

from .filer import *
from .jazzmin import *
from .tinymce import *
from .port import *
from .telegram import *


def debug_port_info():
    """
    Выводит подробную информацию о портах
    """
    printf("<header>=== 🔌 ИНФОРМАЦИЯ О ПОРТАХ ===</header>", style=STYLES)
    
    current_port = get_current_port()
    host, bind_port = get_bind_address()
    
    printf(f"<info>🎯 Текущий порт:</info> <value>{current_port}</value>", style=STYLES)
    printf(f"<info>🏠 Хост:</info> <value>{host}</value>", style=STYLES)
    
    # Проверка занятости порта
    if is_port_in_use(current_port, host):
        printf(f"<warning>⚠️ Порт {current_port} уже используется!</warning>", style=STYLES)
    else:
        printf(f"<success>✅ Порт {current_port} свободен</success>", style=STYLES)
    
    # Список URL для доступа
    urls = get_project_urls()
    printf(f"<info>🌐 Доступные адреса ({len(urls)}):</info>", style=STYLES)
    for i, url in enumerate(urls, 1):
        printf(f"  <success>  {i}. {url}</success>", style=STYLES)
    
    # Информация о окружении
    if 'PORT' in os.environ:
        printf(f"<info>📝 Переменная окружения PORT: {os.environ['PORT']}</info>", style=STYLES)


def debug_telegram():
    """
    Выводит информацию о настройках Telegram
    """
    printf("<header>=== 🤖 TELEGRAM НАСТРОЙКИ ===</header>", style=STYLES)
    
    # Проверяем наличие токена
    token = getattr(sys.modules[__name__], 'TELEGRAM_BOT_TOKEN', None)
    username = getattr(sys.modules[__name__], 'TELEGRAM_BOT_USERNAME', None)
    admin_chat_id = getattr(sys.modules[__name__], 'TELEGRAM_ADMIN_CHAT_ID', None)
    
    # Токен
    if token:
        # Показываем только часть токена для безопасности
        token_preview = f"{token[:10]}...{token[-5:]}" if len(token) > 15 else "Установлен"
        printf(f"<success>✅ TELEGRAM_BOT_TOKEN: <value>{token_preview}</value></success>", style=STYLES)
    else:
        printf(f"<error>❌ TELEGRAM_BOT_TOKEN: <value>НЕ УСТАНОВЛЕН!</value></error>", style=STYLES)
        printf(f"<warning>   💡 Получите токен у @BotFather в Telegram</warning>", style=STYLES)
    
    # Username бота
    if username:
        printf(f"<success>✅ TELEGRAM_BOT_USERNAME: <value>@{username}</value></success>", style=STYLES)
    else:
        printf(f"<warning>⚠️ TELEGRAM_BOT_USERNAME: <value>Не установлен</value></warning>", style=STYLES)
    
    # Admin Chat ID
    if admin_chat_id:
        printf(f"<success>✅ TELEGRAM_ADMIN_CHAT_ID: <value>{admin_chat_id}</value></success>", style=STYLES)
    else:
        printf(f"<warning>⚠️ TELEGRAM_ADMIN_CHAT_ID: <value>Не установлен</value></warning>", style=STYLES)
        printf(f"<warning>   💡 Узнайте свой ID у бота @userinfobot</warning>", style=STYLES)
    
    # Проверяем наличие AUTHENTICATION_BACKENDS
    auth_backends = getattr(sys.modules[__name__], 'AUTHENTICATION_BACKENDS', [])
    if auth_backends:
        printf(f"<info>🔑 AUTHENTICATION_BACKENDS:</info>", style=STYLES)
        for backend in auth_backends:
            printf(f"  <value>  • {backend}</value>", style=STYLES)
    else:
        printf(f"<warning>⚠️ AUTHENTICATION_BACKENDS: <value>Не настроены</value></warning>", style=STYLES)
    
    # Проверяем наличие бота в INSTALLED_APPS
    installed_apps = getattr(sys.modules[__name__], 'INSTALLED_APPS', [])
    if 'telega' in installed_apps or 'apps.telega' in installed_apps:
        printf(f"<success>✅ Приложение 'telega' добавлено в INSTALLED_APPS</success>", style=STYLES)
    else:
        printf(f"<warning>⚠️ Приложение 'telega' НЕ НАЙДЕНО в INSTALLED_APPS</warning>", style=STYLES)


def debug_module_loading(module_name: str, status: str = "loaded", error: str = None):
    """Отладочная информация о загрузке модулей"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    if error:
        printf(f"<error>❌ [{timestamp}] ОШИБКА загрузки {module_name}: {error}</error>", style=STYLES)
    elif status == "loaded":
        printf(f"<success>✅ [{timestamp}] Загружен модуль: {module_name}</success>", style=STYLES)
    elif status == "skipped":
        printf(f"<warning>⚠️ [{timestamp}] Пропущен модуль: {module_name}</warning>", style=STYLES)
    elif status == "config":
        printf(f"<info>🔧 [{timestamp}] Конфигурация: {module_name}</info>", style=STYLES)



# Отладочная информация о путях
def debug_paths():
    """Вывод информации о путях проекта"""
    printf("<header>=== 🗂️ ПУТИ ПРОЕКТА ===</header>", style=STYLES)
    
    paths_data = [
        ["BASE_DIR", str(BASE_DIR)],
        ["APPS_DIR", str(APPS_DIR) if 'APPS_DIR' in globals() else "Не определен"],
        ["STATIC_ROOT", str(STATIC_ROOT) if 'STATIC_ROOT' in globals() else "Не определен"],
        ["MEDIA_ROOT", str(MEDIA_ROOT) if 'MEDIA_ROOT' in globals() else "Не определен"],
        ["Templates DIR", str(APPS_DIR / 'templates')],
    ]
    
    printf_table(paths_data, headers=["Путь", "Значение"], style=STYLES)


# Отладочная информация о настройках
def debug_settings():
    """Вывод информации о настройках Django"""
    printf("<header>=== ⚙️ НАСТРОЙКИ DJANGO ===</header>", style=STYLES)
    
    settings_data = [
        ["DEBUG", str(DEBUG)],
        ["SECRET_KEY", f"{SECRET_KEY[:10]}...{SECRET_KEY[-5:]}" if SECRET_KEY else "Не установлен"],
        ["ALLOWED_HOSTS", ", ".join(ALLOWED_HOSTS) if ALLOWED_HOSTS else "Не установлены"],
        ["LANGUAGE_CODE", str(LANGUAGE_CODE)],
        ["TIME_ZONE", str(TIME_ZONE)],
        ["DEFAULT_CHARSET", str(DEFAULT_CHARSET)],
        ["SECURE_SSL_REDIRECT", str(SECURE_SSL_REDIRECT)],
    ]
    
    printf_table(settings_data, headers=["Параметр", "Значение"], style=STYLES)


# Отладочная информация о приложениях
def debug_apps():
    """Вывод информации о загруженных приложениях"""
    printf("<header>=== 📦 ПРИЛОЖЕНИЯ ===</header>", style=STYLES)
    
    if 'CUSTOM_APPS' in globals():
        printf(f"<success>🎯 Пользовательские приложения ({len(CUSTOM_APPS)}):</success>", style=STYLES)
        for i, app in enumerate(CUSTOM_APPS, 1):
            printf(f"  <info>{i:2d}.</info> <value>{app}</value>", style=STYLES)
    else:
        printf("<warning>⚠️ CUSTOM_APPS не определены</warning>", style=STYLES)
    
    printf("", style=STYLES)  # Пустая строка для разделения
    
    if 'DJANGO_CORE_APPS' in globals():
        printf(f"<success>🎯 Django core приложения ({len(DJANGO_CORE_APPS)}):</success>", style=STYLES)
        for i, app in enumerate(DJANGO_CORE_APPS, 1):
            printf(f"  <info>{i:2d}.</info> <value>{app}</value>", style=STYLES)
    else:
        printf("<warning>⚠️ DJANGO_CORE_APPS не определены</warning>", style=STYLES)
    
    printf("", style=STYLES)  # Пустая строка для разделения
    
    if 'THIRD_PARTY_APPS' in globals():
        printf(f"<success>🎯 Сторонние приложения ({len(THIRD_PARTY_APPS)}):</success>", style=STYLES)
        for i, app in enumerate(THIRD_PARTY_APPS, 1):
            # Добавляем иконки для популярных приложений
            icon = "📦"
            if "jazzmin" in app:
                icon = "🎨"
            elif "tinymce" in app:
                icon = "✏️"
            elif "compressor" in app:
                icon = "🗜️"
            elif "easy_thumbnails" in app:
                icon = "🖼️"
            elif "filer" in app:
                icon = "📁"
            elif "telegram" in app:
                icon = "🤖"
            
            printf(f"  <info>{i:2d}.</info> {icon} <value>{app}</value>", style=STYLES)
    else:
        printf("<warning>⚠️ THIRD_PARTY_APPS не определены</warning>", style=STYLES)


# Отладочная информация о middleware
def debug_middleware():
    """Вывод информации о middleware"""
    printf("<header>=== 🔄 MIDDLEWARE ===</header>", style=STYLES)
    
    if 'MIDDLEWARE' in globals():
        printf(f"<success>📋 Всего middleware: {len(MIDDLEWARE)}</success>", style=STYLES)
        
        # Разделяем на системные и дополнительные
        if 'SYSTEM_MIDDLEWARE' in globals():
            printf(f"<info>🔧 Системные middleware ({len(SYSTEM_MIDDLEWARE)}):</info>", style=STYLES)
            for i, mw in enumerate(SYSTEM_MIDDLEWARE, 1):
                printf(f"  <info>{i:2d}.</info> <value>{mw}</value>", style=STYLES)
        
        if 'ADDITIONAL_MIDDLEWARE' in globals():
            printf(f"<info>🔌 Дополнительные middleware ({len(ADDITIONAL_MIDDLEWARE)}):</info>", style=STYLES)
            for i, mw in enumerate(ADDITIONAL_MIDDLEWARE, 1):
                printf(f"  <info>{i:2d}.</info> <value>{mw}</value>", style=STYLES)
    else:
        printf("<warning>⚠️ MIDDLEWARE не определены</warning>", style=STYLES)


# Отладочная информация о статике
def debug_static():
    """Вывод информации о статических файлах"""
    printf("<header>=== 📁 СТАТИЧЕСКИЕ ФАЙЛЫ ===</header>", style=STYLES)
    
    static_data = [
        ["STATIC_URL", str(STATIC_URL) if 'STATIC_URL' in globals() else "Не определен"],
        ["MEDIA_URL", str(MEDIA_URL) if 'MEDIA_URL' in globals() else "Не определен"],
        ["STATIC_ROOT", str(STATIC_ROOT) if 'STATIC_ROOT' in globals() else "Не определен"],
        ["MEDIA_ROOT", str(MEDIA_ROOT) if 'MEDIA_ROOT' in globals() else "Не определен"],
        ["SASS_PROCESSOR_ENABLED", str(SASS_PROCESSOR_ENABLED) if 'SASS_PROCESSOR_ENABLED' in globals() else "Не определен"],
    ]
    
    printf_table(static_data, headers=["Параметр", "Значение"], style=STYLES)
    
    # Проверяем существование директорий
    printf("<info>📂 Проверка существования директорий:</info>", style=STYLES)
    
    for dir_name, dir_path in [
        ("STATIC_ROOT", STATIC_ROOT if 'STATIC_ROOT' in globals() else None),
        ("MEDIA_ROOT", MEDIA_ROOT if 'MEDIA_ROOT' in globals() else None),
        ("APPS_DIR", APPS_DIR if 'APPS_DIR' in globals() else None),
    ]:
        if dir_path and Path(dir_path).exists():
            printf(f"  <success>✅ {dir_name}: {dir_path}</success>", style=STYLES)
        elif dir_path:
            printf(f"  <warning>⚠️ {dir_name}: {dir_path} (не существует)</warning>", style=STYLES)
        else:
            printf(f"  <error>❌ {dir_name}: не определен</error>", style=STYLES)


# Отладочная информация о кэшировании
def debug_cache():
    """Вывод информации о кэшировании"""
    printf("<header>=== 💾 КЭШИРОВАНИЕ ===</header>", style=STYLES)
    
    if 'CACHES' in globals():
        printf(f"<success>🗄️ Тип кэша: {CACHES['default']['BACKEND'].split('.')[-1]}</success>", style=STYLES)
        
        cache_data = []
        for cache_name, cache_config in CACHES.items():
            backend = cache_config['BACKEND'].split('.')[-1]
            timeout = cache_config.get('TIMEOUT', 'Не задан')
            cache_data.append([cache_name, backend, str(timeout)])
        
        printf_table(cache_data, headers=["Кэш", "Backend", "Timeout"], style=STYLES)
        
        if 'CACHE_MIDDLEWARE_SECONDS' in globals():
            printf(f"<info>⏱️ Middleware кэширования: {CACHE_MIDDLEWARE_SECONDS} сек.</info>", style=STYLES)
    else:
        printf("<warning>⚠️ Настройки кэша не найдены</warning>", style=STYLES)


# Отладочная информация о базах данных
def debug_database():
    """Вывод информации о базах данных"""
    printf("<header>=== 🗄️ БАЗЫ ДАННЫХ ===</header>", style=STYLES)
    
    if 'DATABASES' in globals():
        for db_name, db_config in DATABASES.items():
            engine = db_config['ENGINE'].split('.')[-1]
            db_path = db_config.get('NAME', 'Не указан')
            
            printf(f"<success>📊 {db_name.upper()} БД:</success>", style=STYLES)
            printf(f"  <info>  Движок:</info> <value>{engine}</value>", style=STYLES)
            printf(f"  <info>  Путь:</info> <value>{db_path}</value>", style=STYLES)
            
            # Проверяем существование SQLite БД
            if 'sqlite3' in db_config['ENGINE'] and Path(db_path).exists():
                size = Path(db_path).stat().st_size / 1024 / 1024  # в МБ
                printf(f"  <info>  Размер:</info> <value>{size:.2f} MB</value>", style=STYLES)
    else:
        printf("<warning>⚠️ Настройки БД не найдены</warning>", style=STYLES)


# Основная функция отладки
def debug_all():
    """Выполняет полную отладку всех настроек"""
    printf("<header>═══════════════════════════════════════════════════════════</header>", style=STYLES)
    printf("<header>           🐛 ДЕТАЛЬНАЯ ОТЛАДКА КОНФИГУРАЦИИ                </header>", style=STYLES)
    printf("<header>═══════════════════════════════════════════════════════════</header>", style=STYLES)
    
    start_time = datetime.now()
    printf(f"<info>⏰ Время начала отладки: {start_time.strftime('%Y-%m-%d %H:%M:%S')}</info>", style=STYLES)
    printf("", style=STYLES)
    
    debug_paths()
    printf("", style=STYLES)
    
    debug_settings()
    printf("", style=STYLES)
    
    debug_database()
    printf("", style=STYLES)
    
    debug_cache()
    printf("", style=STYLES)
    
    debug_static()
    printf("", style=STYLES)
    
    debug_apps()
    printf("", style=STYLES)
    
    debug_middleware()
    printf("", style=STYLES)
    
    debug_telegram()  # <-- ДОБАВЛЯЕМ ОТЛАДКУ TELEGRAM
    printf("", style=STYLES)
    
    debug_port_info()
    printf("", style=STYLES)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    printf("<header>═══════════════════════════════════════════════════════════</header>", style=STYLES)
    printf(f"<success>✅ Отладка завершена за {duration:.3f} сек.</success>", style=STYLES)
    printf("<header>═══════════════════════════════════════════════════════════</header>", style=STYLES)


# Основной код при загрузке модуля
if 'runserver' in sys.argv or len(sys.argv) == 1:
    printf("<header>🚀 ЗАПУСК DJANGO ПРОЕКТА 'VisitCard'</header>", style=STYLES)
    printf(f"<info>📅 Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</info>", style=STYLES)
    printf(f"<info>🐍 Python версия: {sys.version.split()[0]}</info>", style=STYLES)
    printf("", style=STYLES)
    
    try:
        from .telegram import *
        debug_module_loading("telegram", "loaded")
    except ImportError as e:
        debug_module_loading("telegram", "error", str(e))
    
    debug_all()
    
    
    
    printf("", style=STYLES)
    printf("<header>=== 🌐 ЗАПУСК СЕРВЕРА ===</header>", style=STYLES)
    
    if DEBUG:
        printf("<warning>⚠️ Режим отладки ВКЛЮЧЕН (только для разработки!)</warning>", style=STYLES)
    else:
        printf("<success>✅ Режим отладки ВЫКЛЮЧЕН (продакшен режим)</success>", style=STYLES)
    
    current_port = get_current_port()
    urls = get_project_urls()
    
    printf(f"<info>🔗 Сервер запущен на порту <value>{current_port}</value></info>", style=STYLES)
    printf(f"<info>🌍 Доступен по адресам:</info>", style=STYLES)
    for url in urls:
        printf(f"  <success>   • {url}</success>", style=STYLES)
    
    if is_port_in_use(current_port):
        printf(f"<error>⚠️ ВНИМАНИЕ! Порт {current_port} может быть занят другим процессом!</error>", style=STYLES)
    
    printf("", style=STYLES)
    printf("<success>✨ Настройки загружены успешно!</success>", style=STYLES)


# Экспортируем отладочные функции
__all__ = [
    'INSTALLED_APPS', 
    "DJANGO_CORE_APPS", 
    "THIRD_PARTY_APPS", 
    "CUSTOM_APPS", 
    "APPS_DIR",
    'debug_all',
    'debug_paths',
    'debug_settings',
    'debug_apps',
    'debug_middleware',
    'debug_static',
    'debug_cache',
    'debug_database',
    'debug_telegram',  # <-- ДОБАВЛЯЕМ
    'get_current_port',
    'get_bind_address',
    'is_port_in_use',
    'get_project_urls',
    'debug_port_info'
]