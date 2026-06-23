TINYMCE_DEFAULT_CONFIG = {
    # САМЫЕ ВАЖНЫЕ НАСТРОЙКИ
    'selector': 'textarea.tinymce',  # ← ДОЛЖЕН совпадать с классом textarea
    'width': '100%',
    'height': 800,
    'menubar': True,
    'statusbar': True,
    'branding': False,
    'promotion': False,
    
    'cache_suffix': '?v=1.0.0',  # Версионирование для кэша
    
    # ВКЛЮЧАЕМ основные плагины (добавлен code)
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview', 'anchor',
        'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'media', 'table', 'help', 'wordcount'
    ],
    
    # ПРОСТАЯ панель инструментов (добавлена кнопка code)
    'toolbar1': 'undo redo | blocks | bold italic underline forecolor backcolor | '
                'alignleft aligncenter alignright alignjustify | '
                'bullist numlist outdent indent | table link image media | '
                'code fullscreen preview help',
    'toolbar2': 'fontfamily fontsize | lineheight | removeformat | '
                'subscript superscript | charmap emoticons | anchor',
    
    'images_upload_url': '/api/upload/image/',  # Ваш эндпоинт
    'images_upload_base_path': '/uploads/',
    'automatic_uploads': True,
    'images_reuse_filename': True,
    
    'table_default_attributes': {
        'border': '1',
        'cellpadding': '5',
        'cellspacing': '0'
    },
    'table_default_styles': {
        'border-collapse': 'collapse',
        'width': '100%'
    },
    
    # БЕЗОПАСНОСТЬ и защита
    'valid_elements': '*[*]',
    'extended_valid_elements': 'span[*]',
    'verify_html': False,
    'cleanup': False,
    'trim_span_elements': False,
    
    # Язык
    'language': 'ru',
    'language_url': '',
    
    # Стили
    'content_style': 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
    
    # Защита Jinja2
    'protect': [
        r'/{%[\s\S]*?%}/g',
        r'/{{[\s\S]*?}}/g',
        r'/{#[\s\S]*?#}/g',
        r'/<\?[\s\S]*?\?>/g',  # PHP теги
        r'/<%[\s\S]*?%>/g',     # ERB/ASP теги
    ],
    
    # Простые настройки форматирования
    'forced_root_block': 'p',
    'force_br_newlines': False,
    'force_p_newlines': True,
    
    # 6. Настройки ссылок
    'relative_urls': False,
    'remove_script_host': True,
    'convert_urls': True,
    'document_base_url': '/',
    
    'link_title': True,
    'link_default_target': '_blank',
    'link_assume_external_targets': True,
    
    'lists_indent_on_tab': True,
    'advlist_number_styles': 'decimal,lower-alpha,upper-alpha,lower-roman,upper-roman',
    
    # Настройки для режима исходного кода
    'codesample_global_prismjs': True,  # Подсветка синтаксиса
    'code_dialog_width': 800,  # Ширина окна редактирования кода
    'code_dialog_height': 600,  # Высота окна редактирования кода
    
    'setup': '''
        function(editor) {
            editor.on('change', function() {
                editor.save();
                jQuery(editor.getElement()).trigger('change');
            });
            editor.on('init', function() {
                console.log('Editor initialized');
            });
        }
    ''',
}