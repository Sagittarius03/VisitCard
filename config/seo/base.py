# config/seo/base.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from abc import ABC, abstractmethod


class BaseSEOModel(ABC):
    """Базовый класс для моделей, которые должны участвовать в SEO"""
    
    @abstractmethod
    def get_absolute_url(self):
        """URL объекта"""
        pass
    
    @abstractmethod
    def get_lastmod(self):
        """Дата последнего изменения"""
        pass
    
    def get_changefreq(self):
        """Частота изменения (по умолчанию weekly)"""
        return 'weekly'
    
    def get_priority(self):
        """Приоритет (по умолчанию 0.5)"""
        return 0.5


class DynamicSitemap(Sitemap):
    """Динамический sitemap, работающий с любыми моделями"""
    
    def __init__(self, model, queryset=None, **kwargs):
        self.model = model
        self.custom_queryset = queryset
        self.changefreq = kwargs.get('changefreq', 'weekly')
        self.priority = kwargs.get('priority', 0.5)
    
    def items(self):
        """Возвращает объекты для sitemap"""
        if self.custom_queryset is not None:
            return self.custom_queryset
        
        queryset = self.model.objects.all()
        
        # Фильтруем по is_published если есть
        if hasattr(self.model, 'is_published'):
            queryset = queryset.filter(is_published=True)
        
        return queryset
    
    def lastmod(self, obj):
        """Дата последнего изменения"""
        if hasattr(obj, 'get_lastmod'):
            return obj.get_lastmod()
        elif hasattr(obj, 'updated_at'):
            return obj.updated_at
        elif hasattr(obj, 'modified'):
            return obj.modified
        elif hasattr(obj, 'published_at'):
            return obj.published_at
        return None
    
    def location(self, obj):
        """URL объекта"""
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return reverse(obj.__class__.__name__.lower(), args=[obj.pk])
    
    def changefreq(self, obj):
        """Частота изменения"""
        if hasattr(obj, 'get_changefreq'):
            return obj.get_changefreq()
        return self.changefreq
    
    def priority(self, obj):
        """Приоритет"""
        if hasattr(obj, 'get_priority'):
            return obj.get_priority()
        return self.priority