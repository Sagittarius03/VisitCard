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

# ============================================================
#  ПОЛУЧАЕМ SITE_URL ИЗ НАСТРОЕК
# ============================================================

try:
    from config.seo.settings import SITE_URL
except ImportError:
    SITE_URL = None


def get_site_url(request=None):
    """Возвращает правильный URL для sitemap"""
    # 🔥 1. Пробуем из глобальных настроек Django
    django_site_url = getattr(settings, 'SITE_URL', None)
    if django_site_url:
        return django_site_url.rstrip('/')
    
    # 🔥 2. Пробуем из config.seo.settings
    if SITE_URL:
        return SITE_URL.rstrip('/')
    
    # 🔥 3. Из request
    if request:
        return request.build_absolute_uri('/').rstrip('/')
    
    # 🔥 4. Фолбэк - используем домен из переменной окружения или настройки
    host_domain = getattr(settings, 'HOST_DOMAIN', None)
    if host_domain:
        return host_domain.rstrip('/')
    
    # 🔥 5. Последний фолбэк
    return 'https://new.legion21kz.com'


# ============================================================
#  ЛЕНИВАЯ ЗАГРУЗКА SITEMAP
# ============================================================

class SitemapLoader:
    def __init__(self):
        self._cache = None
    
    def _load(self):
        if self._cache is None:
            try:
                from config.seo import get_all_sitemaps
                self._cache = get_all_sitemaps()
                print(f"✅ Sitemap загружены: {list(self._cache.keys())}")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки sitemap: {e}")
                self._cache = {}
        return self._cache
    
    def items(self):
        return self._load().items()
    
    def get(self, key, default=None):
        return self._load().get(key, default)
    
    def __getitem__(self, key):
        return self._load()[key]
    
    def __contains__(self, key):
        return key in self._load()
    
    def keys(self):
        return self._load().keys()
    
    def values(self):
        return self._load().values()
    
    def __len__(self):
        return len(self._load())


sitemaps = SitemapLoader()


# ============================================================
#  КАСТОМНЫЕ ВЬЮХИ ДЛЯ SITEMAP
# ============================================================

def sitemap_index(request):
    """Кастомная вьюха для sitemap индекса"""
    sitemaps_dict = sitemaps._load()
    site_url = get_site_url(request)
    
    sections = []
    for section in sitemaps_dict.keys():
        url = f'{site_url}/sitemap-{section}.xml'
        sections.append({
            'location': url,
        })
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for section in sections:
        xml += '  <sitemap>\n'
        xml += f'    <loc>{section["location"]}</loc>\n'
        xml += '  </sitemap>\n'
    xml += '</sitemapindex>'
    
    return HttpResponse(xml, content_type='application/xml')


def sitemap_section(request, section):
    """Кастомная вьюха для отдельного sitemap - ПОЛНОСТЬЮ ПЕРЕРАБОТАННАЯ"""
    sitemaps_dict = sitemaps._load()
    site_url = get_site_url(request)
    
    if section not in sitemaps_dict:
        return HttpResponse(status=404)
    
    sitemap_obj = sitemaps_dict[section]
    
    if not isinstance(sitemap_obj, Sitemap):
        return HttpResponse(status=404)
    
    try:
        items = sitemap_obj.items()
        
        # 🔥 ИСПОЛЬЗУЕМ СПИСОК ДЛЯ СБОРА СТРОК
        xml_parts = []
        xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        url_count = 0
        for item in items:
            try:
                # Получаем location
                location = sitemap_obj.location(item)
                
                # Формируем полный URL
                if location.startswith('/'):
                    full_url = f'{site_url}{location}'
                elif location.startswith('http://') or location.startswith('https://'):
                    full_url = location
                else:
                    full_url = f'{site_url}/{location}'
                
                # Исправляем двойные слеши
                full_url = full_url.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')
                
                # Начинаем тег url
                url_lines = ['  <url>']
                url_lines.append(f'    <loc>{full_url}</loc>')
                
                # lastmod
                try:
                    if hasattr(sitemap_obj, 'lastmod'):
                        lastmod = sitemap_obj.lastmod(item)
                        if lastmod:
                            if hasattr(lastmod, 'date'):
                                lastmod_str = lastmod.date().isoformat()
                            elif hasattr(lastmod, 'isoformat'):
                                lastmod_str = lastmod.isoformat()
                            else:
                                lastmod_str = str(lastmod)
                            url_lines.append(f'    <lastmod>{lastmod_str}</lastmod>')
                except Exception as e:
                    print(f"⚠️ Ошибка lastmod для {item}: {e}")
                    # Пропускаем lastmod, но продолжаем
                
                # changefreq
                try:
                    if hasattr(sitemap_obj, 'changefreq'):
                        changefreq = sitemap_obj.changefreq(item)
                        if changefreq:
                            url_lines.append(f'    <changefreq>{changefreq}</changefreq>')
                except Exception as e:
                    print(f"⚠️ Ошибка changefreq для {item}: {e}")
                
                # priority
                try:
                    if hasattr(sitemap_obj, 'priority'):
                        priority = sitemap_obj.priority(item)
                        if priority is not None:
                            url_lines.append(f'    <priority>{priority}</priority>')
                except Exception as e:
                    print(f"⚠️ Ошибка priority для {item}: {e}")
                
                # 🔥 ВАЖНО: закрываем тег url
                url_lines.append('  </url>')
                
                # Добавляем все строки этого url
                xml_parts.extend(url_lines)
                url_count += 1
                
            except Exception as e:
                print(f"⚠️ Ошибка генерации URL для элемента: {e}")
                # 🔥 ВАЖНО: даже при ошибке, закрываем url если он был открыт
                continue
        
        # 🔥 ВАЖНО: закрываем urlset
        xml_parts.append('</urlset>')
        
        # Объединяем все строки
        xml = '\n'.join(xml_parts)
        
        # 🔥 Проверяем валидность XML (базовая проверка)
        if not xml.endswith('</urlset>'):
            xml += '\n</urlset>'
        
        print(f"✅ Sitemap '{section}' сгенерирован: {url_count} URL-ов")
        
        return HttpResponse(xml, content_type='application/xml')
        
    except Exception as e:
        print(f"❌ Ошибка генерации sitemap для {section}: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(status=500)


urlpatterns = [
    path('robots.txt', robots_view, name='robots'),
    path('sitemap.xml', sitemap_index, {'sitemaps': get_all_sitemaps()}, name='sitemap-index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': get_all_sitemaps()}, name='sitemap'),
    
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