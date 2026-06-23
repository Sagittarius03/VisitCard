# config/seo/robots.py

from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.conf import settings
from .register import seo_registry


class RobotsTxtGenerator:
    """Генератор robots.txt с динамическими правилами"""
    
    def __init__(self):
        self.rules = []
        self.sitemaps = []
    
    def add_rule(self, user_agent, allow=None, disallow=None):
        """Добавление правила для user-agent"""
        self.rules.append({
            'user_agent': user_agent,
            'allow': allow or [],
            'disallow': disallow or [],
        })
    
    def add_sitemap(self, url):
        """Добавление sitemap"""
        self.sitemaps.append(url)
    
    def generate(self):
        """Генерация содержимого robots.txt"""
        lines = []
        
        for rule in self.rules:
            lines.append(f"User-agent: {rule['user_agent']}")
            
            for path in rule['disallow']:
                lines.append(f"Disallow: {path}")
            
            for path in rule['allow']:
                lines.append(f"Allow: {path}")
            
            lines.append("")
        
        for sitemap_url in self.sitemaps:
            lines.append(f"Sitemap: {sitemap_url}")
        
        return "\n".join(lines)
    
    def get_default_rules(self):
        """Правила по умолчанию"""
        
        # Основные правила для всех ботов
        self.add_rule('*', 
            allow=['/'],
            disallow=[
                '/admin/',
                '/search/',
                '/accounts/',
                '/tinymce/',
                '/filer/',
                '/inbound/',
                '/telegram_bot/',
                '/404/',
                '/500/',
                '/*?q=*',
            ]
        )
        
        # Google-specific
        self.add_rule('Googlebot',
            allow=['/'],
            disallow=[]
        )
        
        # Yandex-specific  
        self.add_rule('Yandex',
            allow=['/'],
            disallow=[]
        )
        
        # Sitemap
        self.add_sitemap('/sitemap.xml')


robots_generator = RobotsTxtGenerator()
robots_generator.get_default_rules()


@never_cache
def robots_view(request):
    """Вьюха для robots.txt"""
    for rule in seo_registry.get_robots_rules():
        if callable(rule):
            rule(robots_generator, request)
    
    content = robots_generator.generate()
    return HttpResponse(content, content_type='text/plain')