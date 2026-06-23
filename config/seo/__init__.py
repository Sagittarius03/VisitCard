# config/seo/__init__.py

from .register import seo_registry, register_seo_model
from .sitemaps import get_all_sitemaps, ModelSitemap
from .robots import robots_view, robots_generator


def register_model_for_seo(model, name=None, **kwargs):
    """Быстрая регистрация модели для SEO"""
    from .sitemaps import ModelSitemap
    sitemap_name = name or model.__name__.lower()
    seo_registry.register_sitemap(
        sitemap_name,
        ModelSitemap(model, **kwargs)
    )


def add_static_page(name, url, changefreq='monthly', priority=0.5):
    """Добавление статической страницы в sitemap"""
    seo_registry.register_static_page(name, url, changefreq, priority)


__all__ = [
    'seo_registry',
    'register_seo_model',
    'register_model_for_seo',
    'add_static_page',
    'get_all_sitemaps',
    'robots_view',
    'robots_generator',
]