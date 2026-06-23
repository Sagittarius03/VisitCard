# config/jinja2/env.py

"""
Настройки окружения Jinja2 для проекта Legion21Site.
"""

import os
import hashlib
from django.utils.safestring import mark_safe
from django.contrib.staticfiles import finders

from config import settings
import codecs

# ✅ Функции минификации
def minify_css(content):
    """Простая минификация CSS"""
    try:
        import re
        # Удаляем комментарии
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Удаляем пробелы
        content = re.sub(r'\s+', ' ', content)
        # Удаляем пробелы вокруг скобок
        content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
        return content.strip()
    except:
        return content


def minify_js(content):
    """Простая минификация JS"""
    try:
        import re
        # Удаляем однострочные комментарии
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Удаляем многострочные комментарии
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Удаляем лишние пробелы
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
    except:
        return content


def compress_css(content):
    """Сжимает CSS контент"""
    if settings.DEBUG:
        return content
    
    try:
        # Пытаемся использовать cssmin если установлен
        try:
            from cssmin import cssmin
            return cssmin(content)
        except ImportError:
            return minify_css(content)
    except Exception as e:
        print(f"CSS compression error: {e}")
        return content


def compress_js(content):
    """Сжимает JS контент"""
    if settings.DEBUG:
        return content
    
    try:
        # Пытаемся использовать rjsmin если установлен
        try:
            from rjsmin import jsmin
            return jsmin(content)
        except ImportError:
            return minify_js(content)
    except Exception as e:
        print(f"JS compression error: {e}")
        return content

def strip_bom(content):
    """Удаляет BOM из начала строки, если он есть"""
    if content.startswith(codecs.BOM_UTF8):
        return content[len(codecs.BOM_UTF8):].decode('utf-8')
    return content

def compress_assets(files, kind='css', cache_duration=3600):
    """
    Объединяет и сжимает несколько CSS или JS файлов в один физический файл.
    
    Args:
        files: список путей к файлам (могут быть строки или результаты sass_src)
        kind: 'css' или 'js'
        cache_duration: время кэширования в секундах
    
    Returns:
        HTML теги link или script для production, или отдельные теги для DEBUG
    """
    if not files:
        return mark_safe('')
    
    if settings.DEBUG:
        html_parts = []
        for file_path in files:
            if kind == 'css':
                html_parts.append(f'<link rel="stylesheet" href="{file_path}">')
            else:
                html_parts.append(f'<script src="{file_path}"></script>')
        return mark_safe('\n'.join(html_parts))
    
    try:
        # Собираем содержимое всех файлов с учетом их актуальности
        combined_content = []
        file_hashes = []
        
        for file_path in files:
            # Получаем реальный путь к файлу
            actual_path = file_path
            
            # Убираем /static/ из начала если есть
            if file_path.startswith('/static/'):
                actual_path = file_path[8:]
            
            # Если это результат sass_src, он может содержать параметры
            if '?' in actual_path:
                actual_path = actual_path.split('?')[0]
            
            # Пытаемся найти файл
            found_path = finders.find(actual_path)
            
            if found_path and os.path.exists(found_path):
                with open(found_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    combined_content.append(content)
                    # Хэшируем содержимое каждого файла для отслеживания изменений
                    file_hashes.append(hashlib.md5(content.encode()).hexdigest())
            else:
                print(f"Warning: File not found: {actual_path}")
        
        if not combined_content:
            return mark_safe('')
        
        # Объединяем содержимое
        full_content = '\n'.join(combined_content)
        
        # Сжимаем в зависимости от типа
        if kind == 'css':
            compressed = compress_css(full_content)
            extension = 'css'
        else:
            compressed = compress_js(full_content)
            extension = 'js'
        
        # Создаем уникальное имя файла на основе содержимого и хэшей
        content_hash = hashlib.md5(full_content.encode()).hexdigest()[:12]
        filename = f'compressed_{kind}_{content_hash}.{extension}'
        
        # Путь для сохранения
        compressed_dir = os.path.join(settings.STATIC_ROOT, 'compressed')
        file_path = os.path.join(compressed_dir, filename)
        
        # Создаем директорию если не существует
        os.makedirs(compressed_dir, exist_ok=True)
        
        # Сохраняем файл только если он не существует или изменился
        need_save = True
        if os.path.exists(file_path):
            # Проверяем, не изменилось ли содержимое
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
                if existing_content == compressed:
                    need_save = False
        
        if need_save:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(compressed)
            print(f"Compressed file saved: {filename}")
        
        # Формируем URL к сжатому файлу
        file_url = f'/static/compressed/{filename}'
        
        # Возвращаем соответствующий тег
        if kind == 'css':
            html_result = f'<link rel="stylesheet" href="{file_url}">'
        else:
            html_result = f'<script src="{file_url}"></script>'
        
        return mark_safe(html_result)
        
    except Exception as e:
        print(f"Error compressing assets: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: возвращаем отдельные файлы
        html_parts = [f"Error compressing assets: {e}"]
        for file_path in files:
            if kind == 'css':
                html_parts.append(f'<link rel="stylesheet" href="{file_path}">')
            else:
                html_parts.append(f'<script src="{file_path}"></script>')
        return mark_safe('\n'.join(html_parts))

# ✅ Функция для сохранения сжатых файлов на диск (для production)
def save_compressed_assets(files, kind='css', output_filename=None):
    """
    Сохраняет объединенные и сжатые файлы на диск.
    Используется для офлайн компрессии.
    
    Returns:
        str: URL к сжатому файлу
    """
    if not files:
        return ''
    
    try:
        # Собираем содержимое
        combined_content = []
        for file_path in files:
            actual_path = file_path
            if file_path.startswith('/static/'):
                actual_path = file_path[8:]
            
            found_path = finders.find(actual_path)
            if found_path and os.path.exists(found_path):
                with open(found_path, 'r', encoding='utf-8') as f:
                    combined_content.append(f.read())
        
        if not combined_content:
            return ''
        
        full_content = '\n'.join(combined_content)
        
        # Сжимаем
        if kind == 'css':
            compressed = compress_css(full_content)
            extension = 'css'
        else:
            compressed = compress_js(full_content)
            extension = 'css' if kind == 'css' else 'js'
        
        # Генерируем имя файла если не указано
        if not output_filename:
            content_hash = hashlib.md5(full_content.encode()).hexdigest()[:8]
            output_filename = f'compressed_{kind}_{content_hash}.{extension}'
        
        # Сохраняем в static
        output_path = os.path.join(settings.STATIC_ROOT, 'compressed', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compressed)
        
        # Возвращаем URL
        return f'/static/compressed/{output_filename}'
        
    except Exception as e:
        print(f"Error saving compressed assets: {e}")
        return ''

