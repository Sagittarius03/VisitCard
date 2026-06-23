import os
import sys
from utils.text_format import printf
from config.settings import BASE_DIR

APPS_DIR = BASE_DIR / 'apps'
sys.path.insert(0, str(APPS_DIR))

def get_installed_apps(apps_dir=APPS_DIR, exclude_dirs=None):
    """
    Автоматически находит и возвращает список приложений Django в указанной директории.
    
    Args:
        apps_dir (Path): Путь к папке с приложениями
        exclude_dirs (list): Список папок для исключения
    
    Returns:
        list: Список путей к приложениям Django
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', '__init__', 'migrations']
    
    installed_apps = []
    
    # Проверяем существование директории
    if not apps_dir.exists():
        print(f"⚠️ Папка {apps_dir} не найдена. Создайте папку 'apps' в корне проекта.")
        return installed_apps
    
    # Ищем приложения в папке apps
    for item in apps_dir.iterdir():
        if (item.is_dir() and 
            item.name not in exclude_dirs and
            not item.name.startswith('.') and
            not item.name.startswith('_')):
            
            # Проверяем, является ли папка приложением Django
            if (item / 'apps.py').exists():
                app_name = f"{item.name}"
                installed_apps.append(app_name)
                printf(f"<success>✅ Найдено приложение: {app_name}</success>") if __name__ == '__main__' else None
            else:
                printf(f"<warning>⚠️ Папка '{item.name}' не является приложением Django (отсутствует apps.py)</warning>") if __name__ == '__main__' else None
    
    if not installed_apps:
        printf("<info>ℹ️ В папке 'apps' не найдено приложений Django</info>")
    
    return installed_apps

# Альтернативная версия функции с более строгой проверкой
def get_django_apps(apps_dir=APPS_DIR, required_files=None):
    """
    Более строгая проверка приложений Django.
    
    Args:
        apps_dir (Path): Путь к папке с приложениями
        required_files (list): Обязательные файлы для проверки
    
    Returns:
        list: Список приложений Django
    """
    if required_files is None:
        required_files = ['apps.py', 'models.py', 'views.py']
    
    django_apps = []
    
    if not apps_dir.exists():
        os.makedirs(apps_dir, exist_ok=True)
        print(f"📁 Создана папка {apps_dir}")
        return django_apps
    
    for item in apps_dir.iterdir():
        if (item.is_dir() and 
            not item.name.startswith(('.', '_')) and
            item.name not in ['__pycache__', 'migrations']):
            
            # Проверяем наличие обязательных файлов
            is_django_app = all((item / file).exists() for file in required_files)
            
            if is_django_app:
                app_name = f"apps.{item.name}"
                django_apps.append(app_name)
                print(f"✅ Приложение Django: {app_name}")
            else:
                print(f"❌ Папка '{item.name}' не является приложением Django")
    
    return django_apps

# Функция для получения приложений с настройками из config
def get_apps_with_config(apps_dir=APPS_DIR):
    """
    Получает приложения и их конфигурации.
    
    Returns:
        tuple: (apps_list, apps_configs)
    """
    apps_list = []
    apps_configs = {}
    
    if not apps_dir.exists():
        return apps_list, apps_configs
    
    for item in apps_dir.iterdir():
        if (item.is_dir() and 
            not item.name.startswith(('.', '_')) and
            (item / 'apps.py').exists()):
            
            app_name = f"{item.name}"
            apps_list.append(app_name)
            
            # Пытаемся получить конфиг приложения
            try:
                app_config = f"{app_name}.apps.{item.name.capitalize()}Config"
                apps_configs[app_name] = app_config
            except Exception as e:
                print(f"⚠️ Не удалось получить конфиг для {app_name}: {e}")
                apps_configs[app_name] = app_name
    
    return apps_list, apps_configs

def list_available_apps(apps_dir=APPS_DIR):
    """
    Показывает список доступных приложений.
    
    Returns:
        dict: Информация о приложениях
    """
    apps_info = {}
    
    if not apps_dir.exists():
        return apps_info
    
    for item in apps_dir.iterdir():
        if item.is_dir() and not item.name.startswith(('.', '_')):
            app_info = {
                'name': item.name,
                'is_django_app': (item / 'apps.py').exists(),
                'has_models': (item / 'models.py').exists(),
                'has_views': (item / 'views.py').exists(),
                'has_migrations': (item / 'migrations').exists(),
            }
            apps_info[item.name] = app_info
    
    return apps_info