# config/static/sass.py
from pathlib import Path
from config.settings import BASE_DIR, DEBUG
from config.static.main import STATICFILES_DIRS, STATIC_ROOT
from utils.text_format import printf, STYLES

SASS_PROCESSOR_ENABLED = DEBUG

# Явно укажите, где искать SCSS файлы
SASS_PROCESSOR_INCLUDE_DIRS = [
    BASE_DIR / 'apps' / 'main' / 'static',
]

# Отключите поиск в других приложениях
SASS_PROCESSOR_AUTO_INCLUDE = False

# Укажите, куда сохранять скомпилированные CSS
SASS_PROCESSOR_ROOT = STATIC_ROOT / 'css'

# Функция для проверки и создания директории
def ensure_sass_processor_root():
    """
    Проверяет существование SASS_PROCESSOR_ROOT и создает его при необходимости
    Returns:
        bool: True если директория существует или создана, False в случае ошибки
    """
    try:
        if SASS_PROCESSOR_ROOT.exists():
            printf(f"<success>✅ SASS процессор: директория существует</success>", style=STYLES)
            printf(f"  <info>📁 Путь: {SASS_PROCESSOR_ROOT}</info>", style=STYLES)
            return True
        else:
            printf(f"<warning>⚠️ SASS процессор: директория не найдена</warning>", style=STYLES)
            printf(f"  <info>📁 Создаю: {SASS_PROCESSOR_ROOT}</info>", style=STYLES)
            
            # Создаем директорию и все родительские папки
            SASS_PROCESSOR_ROOT.mkdir(parents=True, exist_ok=True)
            
            # Проверяем, что директория успешно создана
            if SASS_PROCESSOR_ROOT.exists():
                printf(f"<success>✅ Директория успешно создана</success>", style=STYLES)
                return True
            else:
                printf(f"<error>❌ Не удалось создать директорию</error>", style=STYLES)
                return False
                
    except PermissionError:
        printf(f"<error>❌ Ошибка доступа: недостаточно прав для создания {SASS_PROCESSOR_ROOT}</error>", style=STYLES)
        return False
    except Exception as e:
        printf(f"<error>❌ Ошибка при создании директории: {e}</error>", style=STYLES)
        return False

# Функция для очистки скомпилированных CSS файлов
def clean_sass_processor_root():
    """
    Очищает директорию SASS_PROCESSOR_ROOT от всех CSS файлов
    Returns:
        int: Количество удаленных файлов
    """
    if not SASS_PROCESSOR_ROOT.exists():
        printf(f"<warning>⚠️ Директория не существует: {SASS_PROCESSOR_ROOT}</warning>", style=STYLES)
        return 0
    
    deleted_count = 0
    try:
        for file in SASS_PROCESSOR_ROOT.glob('*.css'):
            file.unlink()
            deleted_count += 1
            printf(f"  <info>🗑️ Удален: {file.name}</info>", style=STYLES)
        
        if deleted_count > 0:
            printf(f"<success>✅ Удалено {deleted_count} CSS файлов</success>", style=STYLES)
        else:
            printf(f"<info>ℹ️ Нет файлов для удаления</info>", style=STYLES)
        
        return deleted_count
    except Exception as e:
        printf(f"<error>❌ Ошибка при очистке: {e}</error>", style=STYLES)
        return 0

# Функция для получения информации о директории
def get_sass_processor_info():
    """
    Возвращает информацию о директории SASS_PROCESSOR_ROOT
    Returns:
        dict: Информация о директории
    """
    info = {
        'exists': False,
        'path': str(SASS_PROCESSOR_ROOT),
        'files_count': 0,
        'total_size': 0,
        'files': []
    }
    
    if SASS_PROCESSOR_ROOT.exists():
        info['exists'] = True
        try:
            # Собираем информацию о CSS файлах
            for file in SASS_PROCESSOR_ROOT.glob('*.css'):
                file_stat = file.stat()
                info['files_count'] += 1
                info['total_size'] += file_stat.st_size
                info['files'].append({
                    'name': file.name,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime
                })
        except Exception as e:
            printf(f"<error>❌ Ошибка при чтении директории: {e}</error>", style=STYLES)
    
    return info

# Функция для отладки SASS настроек
def debug_sass_settings():
    """Выводит отладочную информацию о SASS настройках"""
    printf("<header>=== 🎨 SASS НАСТРОЙКИ ===</header>", style=STYLES)
    
    printf(f"<info>🔧 SASS_PROCESSOR_ENABLED:</info> <value>{SASS_PROCESSOR_ENABLED}</value>", style=STYLES)
    printf(f"<info>📁 SASS_PROCESSOR_ROOT:</info> <value>{SASS_PROCESSOR_ROOT}</value>", style=STYLES)
    printf(f"<info>🔍 SASS_PROCESSOR_AUTO_INCLUDE:</info> <value>{SASS_PROCESSOR_AUTO_INCLUDE}</value>", style=STYLES)
    
    printf(f"<info>📂 Директории поиска SCSS:</info>", style=STYLES)
    for include_dir in SASS_PROCESSOR_INCLUDE_DIRS:
        if include_dir.exists():
            printf(f"  <success>✅ {include_dir}</success>", style=STYLES)
        else:
            printf(f"  <warning>⚠️ {include_dir} (не существует)</warning>", style=STYLES)
    
    # Проверяем и создаем директорию
    ensure_sass_processor_root()
    
    # Показываем информацию о директории
    info = get_sass_processor_info()
    if info['exists']:
        printf(f"<info>📊 Статистика SASS директории:</info>", style=STYLES)
        printf(f"  <info>  Файлов:</info> <value>{info['files_count']}</value>", style=STYLES)
        
        if info['total_size'] > 0:
            size_kb = info['total_size'] / 1024
            size_mb = size_kb / 1024
            if size_mb >= 1:
                printf(f"  <info>  Размер:</info> <value>{size_mb:.2f} MB</value>", style=STYLES)
            else:
                printf(f"  <info>  Размер:</info> <value>{size_kb:.2f} KB</value>", style=STYLES)
        
        if info['files'] and DEBUG:
            printf(f"<info>📄 Список файлов:</info>", style=STYLES)
            for file_info in info['files'][:10]:  # Показываем первые 10
                size_kb = file_info['size'] / 1024
                printf(f"  <info>  • {file_info['name']}</info> <value>({size_kb:.1f} KB)</value>", style=STYLES)
            if len(info['files']) > 10:
                printf(f"  <info>  ... и {len(info['files']) - 10} других</info>", style=STYLES)
    else:
        printf(f"<warning>⚠️ Директория не создана</warning>", style=STYLES)

# Выполняем проверку при импорте модуля (если не в тестах)
if __name__ != '__main__':
    # Автоматически проверяем и создаем директорию при загрузке
    if SASS_PROCESSOR_ENABLED:
        ensure_sass_processor_root()

# Добавляем SASS_PROCESSOR_ROOT в STATICFILES_DIRS
if SASS_PROCESSOR_ROOT not in STATICFILES_DIRS:
    STATICFILES_DIRS.append(SASS_PROCESSOR_ROOT)