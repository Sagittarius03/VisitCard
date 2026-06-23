import re
from django.utils.safestring import mark_safe
from django.core.cache import cache
from config import settings

from django.template import Context

import codecs

def get_module_model():
    """Ленивая загрузка модели Module для избежания циклических импортов"""
    from django.apps import apps
    return apps.get_model('main', 'Module')



def render_modules(position, request=None):
    """Рендерит все активные модули для указанной позиции."""
    if not request:
        return mark_safe('')
    
    try:
        Module = get_module_model()
        
        page_slug = None
        if hasattr(request, 'resolver_match'):
            if request.resolver_match and request.resolver_match.url_name == 'page_detail':
                page_slug = request.resolver_match.kwargs.get('slug')
        
        cache_key = f'modules_{position}_{page_slug or "all"}'
        rendered = cache.get(cache_key)
        
        if rendered is None:
            modules = Module.objects.filter(
                position=position,
                is_active=True
            ).order_by('order')
            
            html_parts = []
            for module in modules:
                if module.should_display(page_slug):
                    content = module.get_rendered_content()
                    html_parts.append(mark_safe(content))
            
            rendered = mark_safe('\n'.join(html_parts))
            cache.set(cache_key, rendered, 3600)
        
        return rendered
    except Exception as e:
        print(f"Error rendering modules at {position}: {e}")
        return mark_safe('')

def render_modules_in_content(content, request=None):
    """
    Заменяет метки {{module:название_модуля}} на HTML код модуля.
    Используется для вставки модулей прямо в контент страницы через TinyMCE.
    
    Поддерживаемые форматы:
    - {{module:Имя модуля}}
    - {{module:5}} (по ID модуля)
    - {{module:Имя модуля|param1=value1|param2=value2}} (с параметрами)
    """
    if not content:
        return content
    
    def replace_module(match):
        module_ref = match.group(1).strip()
        
        # Парсим параметры если есть
        parts = module_ref.split('|')
        module_name = parts[0]
        
        params = {}
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                params[key.strip()] = value.strip()
        
        try:
            Module = get_module_model()
            
            # Поиск модуля по имени или ID
            if module_name.isdigit():
                module = Module.objects.get(id=int(module_name), is_active=True, position='inline')
            else:
                module = Module.objects.get(name=module_name, is_active=True, position='inline')
            
            # Получаем slug текущей страницы
            page_slug = None
            if request and hasattr(request, 'resolver_match'):
                if request.resolver_match and request.resolver_match.url_name == 'page_detail':
                    page_slug = request.resolver_match.kwargs.get('slug')
            
            # Проверяем, должен ли модуль отображаться
            if module.should_display(page_slug):
                content_html = module.get_rendered_content()
                
                # Заменяем параметры в контенте модуля
                for key, value in params.items():
                    content_html = content_html.replace(f'{{{{ {key} }}}}', value)
                    content_html = content_html.replace(f'{{{{ {key}|safe }}}}', mark_safe(value))
                
                return content_html
            return ''
            
        except Exception as e:
            if settings.DEBUG:
                print(f"Module error: {module_ref} - {e}")
            return f'<!-- Module "{module_name}" not found or inactive -->'
    
    # Регулярное выражение для поиска меток {{module:...}}
    pattern = r'\{\{\s*module:([^}]+?)\s*\}\}'
    result = re.sub(pattern, replace_module, content)
    
    return mark_safe(result)

def get_inline_modules_info():
    """Возвращает список всех inline-модулей для отображения в админке"""
    try:
        Module = get_module_model()
        modules = Module.objects.filter(position='inline', is_active=True)
        return [
            {
                'name': m.name,
                'id': m.id,
                'code': f'{{{{module:{m.name}}}}}',
                'code_by_id': f'{{{{module:{m.id}}}}}'
            }
            for m in modules
        ]
    except:
        return []
def has_modules(position):
    """Проверяет, есть ли модули в указанной позиции"""
    try:
        Module = get_module_model()
        return Module.objects.filter(position=position, is_active=True).exists()
    except:
        return False

