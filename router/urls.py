from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from django.views.static import serve
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from config.seo import get_all_sitemaps, robots_view

from django.http import HttpResponse
from .urls_loader import load_custom_apps_urls


urlpatterns = [
    # path('robots.txt', robots_view, name='robots'),
    # path('sitemap.xml', sitemap_index, {'sitemaps': get_all_sitemaps()}, name='sitemap-index'),
    # path('sitemap-<section>.xml', sitemap, {'sitemaps': get_all_sitemaps()}, name='sitemap'),
    
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('filer/', include('filer.urls')),
]

urlpatterns += load_custom_apps_urls() or [path("", lambda request: HttpResponse("Нет URL"),)]

# Подключаем статику и медиа в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': False
        }),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': False
        }),
    ]