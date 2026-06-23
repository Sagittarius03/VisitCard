class ConditionalXFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Разрешенные домены для встраивания
        self.allowed_referrers = [
            # Яндекс
            'webvisor.com',
            'metrika.yandex',
            'yandex.ru',
            
            # Google
            'google.com',
            'googleapis.com',
            'google-analytics.com',
            'googletagmanager.com',
            'doubleclick.net',  # Google Ads
            'youtube.com',       # YouTube встраивание
            
            # Другие популярные сервисы
            'facebook.com',
            'vk.com',
            'instagram.com',
            'twitter.com',
            
            # Ваши доверенные домены (если нужно)
            # 'your-trusted-site.com',
        ]

    def __call__(self, request):
        response = self.get_response(request)
        
        # Получаем Referer
        referer = request.META.get('HTTP_REFERER', '')
        
        # Проверяем, разрешен ли реферер
        if referer and self.is_allowed_referer(referer):
            # Не добавляем заголовок — разрешаем встраивание
            return response
        
        # Для всех остальных — строгий запрет
        response['X-Frame-Options'] = 'DENY'
        return response
    
    def is_allowed_referer(self, referer):
        """Проверяет, разрешен ли данный referer"""
        referer_lower = referer.lower()
        
        for allowed in self.allowed_referrers:
            if allowed in referer_lower:
                return True
        
        return False