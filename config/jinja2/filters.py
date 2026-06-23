# config/jinja2/filters.py

import json
from django.utils.safestring import mark_safe


def safe_json(value):
    """
    Сериализует Python объект в JSON без экранирования Unicode.
    Сохраняет русские символы и другие UTF-8 символы.
    
    Использование в шаблоне:
    {{ page_schema|safe_json }}
    
    Args:
        value: Любой сериализуемый Python объект (dict, list, str, int, etc.)
    
    Returns:
        mark_safe: HTML-safe JSON строка с русскими символами
    """
    if value is None:
        return 'null'
    
    # ensure_ascii=False - сохраняет русские символы
    # separators=(',', ':') - убирает лишние пробелы для минификации
    json_str = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    
    return mark_safe(json_str)


def minify_json(value):
    """
    Минифицирует JSON строку (убирает пробелы).
    Полезно для больших JSON структур.
    
    Использование:
    {{ json_string|minify_json }}
    """
    if not value:
        return ''
    
    try:
        # Парсим и снова сериализуем без пробелов
        parsed = json.loads(value)
        return json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
    except (json.JSONDecodeError, TypeError):
        return value


def pretty_json(value):
    """
    Форматирует JSON с отступами для читаемости (только для отладки).
    
    Использование:
    {{ data|pretty_json }}
    """
    if value is None:
        return 'null'
    
    # Для отладки используем отступы
    json_str = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    
    return mark_safe(json_str)


def js_escape(value):
    """
    Экранирует строку для безопасного использования в JavaScript.
    
    Использование:
    {{ user_input|js_escape }}
    """
    if not value:
        return ''
    
    # Заменяем опасные символы
    escapes = {
        '\\': '\\\\',
        "'": "\\'",
        '"': '\\"',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '</': '<\\/',
    }
    
    result = str(value)
    for char, escaped in escapes.items():
        result = result.replace(char, escaped)
    
    return mark_safe(result)