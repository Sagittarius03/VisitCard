# config/middleware/jinja2.py
from django.template import engines

class Jinja2GlobalRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # ✅ Используем квадратные скобки, как в словаре
        try:
            self.jinja2_engine = engines['jinja2']
        except KeyError:
            # Если движок не найден, просто пропускаем
            self.jinja2_engine = None
    
    def __call__(self, request):
        # Добавляем request в глобальные переменные Jinja2
        if self.jinja2_engine and hasattr(self.jinja2_engine, 'env'):
            self.jinja2_engine.env.globals['request'] = request
        
        response = self.get_response(request)
        return response