# config/seo/sitemaps.py - ПОЛНАЯ ЗАМЕНА

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    """Sitemap для статических страниц"""
    
    def __init__(self, pages):
        self.pages = pages
    
    def items(self):
        return self.pages
    
    def location(self, item):
        return item['url']
    
    def changefreq(self, item):
        return item.get('changefreq', 'monthly')
    
    def priority(self, item):
        return item.get('priority', 0.5)


class ModelSitemap(Sitemap):
    """Sitemap для модели с полной поддержкой всех полей"""
    
    def __init__(self, model, **kwargs):
        self.model = model
        self._default_changefreq = kwargs.get('changefreq', 'weekly')
        self._default_priority = kwargs.get('priority', 0.5)
        self._custom_queryset = kwargs.get('queryset', None)
    
    def items(self):
        """Возвращает только опубликованные страницы"""
        try:
            if self._custom_queryset is not None:
                return self._custom_queryset
            
            queryset = self.model.objects.all()
            
            if hasattr(self.model, 'is_published'):
                queryset = queryset.filter(is_published=True)
            
            if hasattr(self.model, 'exclude_from_sitemap'):
                queryset = queryset.filter(exclude_from_sitemap=False)
            
            return queryset
        except Exception as e:
            print(f"⚠️ Ошибка получения items для {self.model.__name__}: {e}")
            return self.model.objects.none()
    
    def lastmod(self, obj):
        """Дата последнего изменения"""
        try:
            if hasattr(obj, 'updated_at') and obj.updated_at:
                return obj.updated_at
            if hasattr(obj, 'published_at') and obj.published_at:
                return obj.published_at
            if hasattr(obj, 'created_at') and obj.created_at:
                return obj.created_at
        except Exception:
            pass
        return timezone.now()
    
    def location(self, obj):
        """URL объекта"""
        try:
            if hasattr(obj, 'get_absolute_url'):
                return obj.get_absolute_url()
            return reverse(obj.__class__.__name__.lower(), args=[obj.pk])
        except Exception:
            return f"/{obj.pk}/"
    
    def changefreq(self, obj):
        """
        Частота обновления страницы
        """
        try:
            if hasattr(obj, 'get_changefreq') and callable(obj.get_changefreq):
                return obj.get_changefreq()
        except Exception:
            pass
        
        # Возвращаем значение по умолчанию
        return self._default_changefreq
    
    def priority(self, obj):
        """
        Приоритет страницы (0.0 - 1.0)
        """
        try:
            if hasattr(obj, 'get_priority') and callable(obj.get_priority):
                return obj.get_priority()
        except Exception:
            pass
        
        # Возвращаем значение по умолчанию
        return self._default_priority


# Глобальный словарь для хранения всех sitemap
_sitemaps_cache = None


def get_all_sitemaps():
    """
    Собирает все зарегистрированные sitemap
    """
    global _sitemaps_cache
    
    if _sitemaps_cache is not None:
        return _sitemaps_cache
    
    sitemaps = {}
    
    try:
        from .register import seo_registry
        sitemaps.update(seo_registry.get_sitemaps())
        
        static_pages = seo_registry.get_static_pages()
        if static_pages:
            sitemaps['static'] = StaticViewSitemap(static_pages)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки sitemap: {e}")
    
    _sitemaps_cache = sitemaps
    return sitemaps