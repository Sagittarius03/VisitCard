# config/seo/register.py

class SEORegistry:
    """Регистратор для всех SEO-объектов"""
    
    def __init__(self):
        self.sitemaps = {}
        self.static_pages = []
        self.dynamic_rules = []
    
    def register_sitemap(self, name, sitemap):
        """Регистрация sitemap для модели - без обращения к БД"""
        # Проверяем, не зарегистрирован ли уже
        if name in self.sitemaps:
            print(f"ℹ️ Sitemap '{name}' уже зарегистрирован, пропускаем")
            return
        
        # Регистрируем без вызова items()
        self.sitemaps[name] = sitemap
        print(f"✅ Sitemap '{name}' зарегистрирован")
    
    def register_static_page(self, name, url, changefreq='monthly', priority=0.5):
        """Регистрация статической страницы"""
        self.static_pages.append({
            'name': name,
            'url': url,
            'changefreq': changefreq,
            'priority': priority,
        })
        print(f"✅ Статическая страница '{name}' зарегистрирована")
    
    def register_robots_rule(self, rule):
        """Регистрация правила для robots.txt"""
        self.dynamic_rules.append(rule)
    
    def get_sitemaps(self):
        """Получение всех sitemap"""
        return self.sitemaps
    
    def get_robots_rules(self):
        """Получение всех правил для robots.txt"""
        return self.dynamic_rules
    
    def get_static_pages(self):
        """Получение статических страниц для sitemap"""
        return self.static_pages
    
    def is_empty(self):
        """Проверка, есть ли зарегистрированные sitemap"""
        return len(self.sitemaps) == 0


# Глобальный экземпляр регистратора
seo_registry = SEORegistry()


def register_seo_model(model, name=None, **kwargs):
    """
    Декоратор для регистрации модели в SEO
    
    Использование:
    @register_seo_model(Post, 'blog', changefreq='daily', priority=0.8)
    class Post(models.Model):
        ...
    """
    def decorator(model_class):
        from .sitemaps import ModelSitemap
        sitemap_name = name or model_class.__name__.lower()
        seo_registry.register_sitemap(
            sitemap_name,
            ModelSitemap(model_class, **kwargs)
        )
        return model_class
    return decorator