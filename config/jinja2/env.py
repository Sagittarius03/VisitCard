# config/jinja2/env.py

"""
Настройки окружения Jinja2 для проекта Legion21Site.
"""

from time import timezone

import jinja2

from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.urls import reverse
from django.utils import translation
from django.contrib.messages import get_messages
from django.contrib.staticfiles.storage import staticfiles_storage

from sass_processor.processor import sass_processor
from config import settings

from datetime import datetime

from .compress import *
from .module import *

from .filters import safe_json, minify_json, pretty_json, js_escape 


def environment(**options):
    """
    Создает окружение Jinja2 с дополнительными функциями и фильтрами.
    """
    extensions = list(options.get('extensions', []))
    
    # Добавляем расширение sass_processor
    try:
        extensions.append('sass_processor.jinja2.ext.SassSrc')
    except Exception as e:
        print(f"Warning: Could not add sass_processor extension: {e}")
    
    options['extensions'] = extensions
    
    # Создаем окружение
    env = jinja2.Environment(**options)
    
    # ✅ Добавляем глобальные функции
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'sass_src': lambda path: sass_processor(path),
        'get_current_language': translation.get_language,
        'get_messages': get_messages,
        'render_modules': render_modules,
        'has_modules': has_modules,
        'mark_safe': mark_safe,
        'compress_assets': compress_assets,
        'render_modules_in_content': render_modules_in_content,
        'get_inline_modules_info': get_inline_modules_info,
        'now': datetime.now
    })
    
    # ✅ Добавляем фильтры для сжатия (существующие)
    env.filters.update({
        'compress_css': compress_css,
        'compress_js': compress_js,
        'minify_css': minify_css,
        'minify_js': minify_js,
    })
    
    # ✅ ДОБАВЛЯЕМ НОВЫЕ ФИЛЬТРЫ ДЛЯ JSON
    env.filters.update({
        'safe_json': safe_json,      # ← ОСНОВНОЙ ФИЛЬТР ДЛЯ JSON
        'minify_json': minify_json,  # Для минификации JSON строк
        'pretty_json': pretty_json,  # Для отладки
        'js_escape': js_escape,      # Для экранирования JS
    })
    
    # Функция для CSRF токена
    def csrf_token():
        from django.template.context_processors import csrf
        request = jinja2.utils.MissingType('request')
        context = csrf({'request': request})
        return context.get('csrf_token', '')
    
    env.globals['csrf_token'] = csrf_token
    
    # Добавляем DEBUG в глобальные переменные для шаблонов
    env.globals['DEBUG'] = settings.DEBUG
    
    # Добавляем стандартные фильтры Django
    from django.template.defaultfilters import (
        date, time, timesince, timeuntil, 
        floatformat, truncatechars, truncatewords,
        pluralize, phone2numeric, filesizeformat,
        safe, linebreaks, linebreaksbr, urlize,
        striptags, title, upper, lower, capfirst
    )
    
    env.filters.update({
        'date': date,
        'time': time,
        'timesince': timesince,
        'timeuntil': timeuntil,
        'floatformat': floatformat,
        'truncatechars': truncatechars,
        'truncatewords': truncatewords,
        'pluralize': pluralize,
        'phone2numeric': phone2numeric,
        'filesizeformat': filesizeformat,
        'safe': safe,
        'linebreaks': linebreaks,
        'linebreaksbr': linebreaksbr,
        'urlize': urlize,
        'striptags': striptags,
        'title': title,
        'upper': upper,
        'lower': lower,
        'capfirst': capfirst,
    })
    
    return env