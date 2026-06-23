JAZZMIN_SETTINGS = {
    # --- Настройка темы (переключение по системе) ---
    # "light" - всегда светлая тема
    # "dark" - всегда тёмная тема
    # "auto" - автоматически переключается в зависимости от темы вашей ОС
    "default_theme_mode": "auto",
    
    # Название вкладки браузера и заголовки
    "site_title": "Legion21 Админка",
    "site_header": "Legion21",
    "site_brand": "Legion21 CMS",
    # "site_logo": '/static/main/icon/favicon.svg',     
    "site_icon": '/static/main/icon/favicon-32x32.png',  # Фавикон (32x32 px)# Путь к вашему логотипу
    
    
    # Приветствие на странице входа
    "welcome_sign": "Добро пожаловать в Legion21 CMS",
    
    # Копирайт в футере
    "copyright": "Legion21",
    
    # Показывать иконку переключения темы в шапке (удобно для тестирования)
    "show_theme_chooser": True,  # <-- Позволяет быстро переключаться
    "changeform_format": "vertical_tabs",      # Вертикальные вкладки (слева)
    
    
    "show_changeform_tab": False,
    
    "custom_css": "admin/css/filer-dark-theme-fix.css",
}

# Настройки внешнего вида (более тонкая настройка)
JAZZMIN_UI_TWEAKS = {
    # Здесь тоже можно задать тему, но используйте "theme": "flatly",
    # а для переключения используйте default_theme_mode выше.
    # Обратите внимание: параметр "dark_mode_theme" больше не используется [citation:1][citation:2][citation:10].
    
    # Пример дополнительной настройки (необязательно):
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,  # Убедитесь, что этот параметр отсутствует или установлен в None
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}