import importlib
import sys
from pathlib import Path
from django.urls import include, path
from django.conf import settings

from utils.text_format import printf


# Конфигурация приоритетов загрузки
APP_PRIORITY = {
    # Основные приложения (высший приоритет - загружаются первыми)
    'core': 100,
    'main': 100,
    
    # Публичные приложения (средний приоритет)
    'blog': 80,
    'portfolio': 80,
    'skills': 80,
    
    # Дополнительные приложения
    'roadmap': 70,
    'checklist': 70,
    'reading': 70,
    'vscode_config': 70,
    
    # Обратная связь и пользователи
    'feedback': 60,
    'users': 60,
    
    # Вспомогательные приложения (низший приоритет)
    'telegram_bot': 50,
    'api': 40,
    'admin': 30,
}


def get_app_priority(app_name):
    """Получает приоритет приложения"""
    # Убираем префикс apps. если есть
    clean_name = app_name.replace('apps.', '')
    return APP_PRIORITY.get(clean_name, 50)


def load_custom_apps_urls():
    """
    Автоматически подключает URL-маршруты из приложений в папке apps/
    с учетом приоритетов загрузки.
    
    Ищет в каждом приложении из CUSTOM_APPS файлы:
    - urls.py (основной файл маршрутов)
    - router.py (для DRF или кастомных роутеров)
    
    Возвращает список URL-паттернов для include в основной urls.py
    """
    url_patterns = []
    
    # Проверяем наличие константы в настройках
    custom_apps = getattr(settings, 'CUSTOM_APPS', [])
    
    if not custom_apps:
        printf("<warning>⚠️  CUSTOM_APPS не найден в настройках</warning>")
        return url_patterns
    
    # Добавляем apps в путь если его там нет
    apps_path = Path(settings.BASE_DIR) / 'apps'
    if str(apps_path) not in sys.path:
        sys.path.insert(0, str(apps_path))
    
    # Сортируем приложения по приоритету (от высшего к низшему)
    sorted_apps = sorted(custom_apps, key=get_app_priority, reverse=True)
    
    printf("<info>📋 Загрузка URL-маршрутов по приоритету:</info>")
    for app in sorted_apps:
        priority = get_app_priority(app)
        printf(f"  • {app} (приоритет: {priority})")
    
    for app_name in sorted_apps:
        app_urls = None
        
        # Пробуем импортировать urls.py
        try:
            urls_module = importlib.import_module(f'{app_name}.urls')
            app_urls = getattr(urls_module, 'urlpatterns', None)
            
            if app_urls:
                # Получаем префикс из конфига
                url_prefix = get_app_url_prefix(app_name)
                
                # Проверяем, есть ли пространство имен
                if hasattr(urls_module, 'app_name'):
                    url_patterns.append(
                        path(f'{url_prefix}', include(f'{app_name}.urls'))
                    )
                    printf(f"<success>✅ {app_name}: /{url_prefix} (с namespace)</success>")
                else:
                    url_patterns.append(
                        path(f'{url_prefix}', include(f'{app_name}.urls'))
                    )
                    printf(f"<success>✅ {app_name}: /{url_prefix}</success>")
                
        except ImportError as e:
            # Если нет urls.py, пробуем найти router.py
            try:
                router_module = importlib.import_module(f'{app_name}.router')
                router = getattr(router_module, 'router', None)
                
                if router:
                    # Для DRF роутеров
                    url_prefix = get_app_url_prefix(app_name)
                    url_patterns.append(
                        path(f'{url_prefix}', include(router.urls))
                    )
                    printf(f"<success>✅ {app_name}: /{url_prefix} (DRF router)</success>")
                else:
                    printf(f"<warning>⚠️  {app_name}: нет router или urlpatterns</warning>")
                    
            except ImportError:
                # Проверяем, может быть приложение не должно иметь URL
                if app_name not in ['telegram_bot']:  # Исключения
                    printf(f"<warning>⚠️  {app_name}: не найдены файлы urls.py или router.py</warning>")
                
        except Exception as e:
            printf(f"<error>❌ {app_name}: ошибка - {e}</error>")
    
    printf("<info>✅ Все URL-маршруты загружены</info>")
    return url_patterns


def get_app_url_prefix(app_name):
    """
    Получает префикс URL для приложения.
    Можно кастомизировать по-разному:
    - из конфига приложения
    - из названия приложения
    - из специального атрибута в приложении
    """
    
    # Убираем префикс apps. если есть
    clean_name = app_name.replace('apps.', '')
    
    # Способ 1: Пробуем импортировать конфиг приложения
    try:
        app_config_module = importlib.import_module(f'{app_name}.apps')
        config_class = getattr(app_config_module, f'{clean_name.capitalize()}Config', None)
        
        if config_class and hasattr(config_class, 'url_prefix'):
            return config_class.url_prefix
    except ImportError:
        pass
    
    # Способ 2: Специальные префиксы для некоторых приложений
    special_prefixes = {
        'core': '',
        'main': '',
        'blog': 'blog/',
        'portfolio': 'portfolio/',
        'skills': 'skills/',
        'roadmap': 'roadmap/',
        'checklist': 'checklist/',
        'reading': 'reading/',
        'vscode_config': 'vscode/',
        'feedback': 'feedback/',
        'users': 'users/',
        'telegram_bot': 'telegram-bot/',
    }
    
    if clean_name in special_prefixes:
        return special_prefixes[clean_name]
    
    # Способ 3: Используем название приложения как префикс
    return f'{clean_name}/'


def load_custom_apps_urls_with_namespaces():
    """
    Подключает маршруты с пространствами имен
    """
    url_patterns = []
    custom_apps = getattr(settings, 'CUSTOM_APPS', [])
    
    # Сортируем по приоритету
    sorted_apps = sorted(custom_apps, key=get_app_priority, reverse=True)
    
    for app_name in sorted_apps:
        try:
            # Проверяем существует ли urls.py
            urls_module = importlib.import_module(f'{app_name}.urls')
            
            # Проверяем наличие app_name в urls.py
            app_namespace = getattr(urls_module, 'app_name', None)
            if not app_namespace:
                app_namespace = app_name.replace('apps.', '')
            
            url_prefix = get_app_url_prefix(app_name)
            
            # Добавляем с пространством имен
            url_patterns.append(
                path(
                    f'{url_prefix}', 
                    include((f'{app_name}.urls', app_namespace), namespace=app_namespace)
                )
            )
            printf(f"<success>✅ {app_name}: /{url_prefix} (namespace='{app_namespace}')</success>")
            
        except ImportError:
            continue
        except Exception as e:
            printf(f"<error>❌ {app_name}: ошибка - {e}</error>")
    
    return url_patterns


def get_urls_info():
    """
    Возвращает информацию о всех зарегистрированных URL для отладки
    """
    custom_apps = getattr(settings, 'CUSTOM_APPS', [])
    result = []
    
    for app_name in custom_apps:
        priority = get_app_priority(app_name)
        prefix = get_app_url_prefix(app_name)
        result.append({
            'app': app_name,
            'priority': priority,
            'prefix': prefix,
        })
    
    # Сортируем по приоритету
    return sorted(result, key=lambda x: x['priority'], reverse=True)