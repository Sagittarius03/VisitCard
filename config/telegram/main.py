# Telegram Bot настройки
import os


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
TELEGRAM_AUTO_START = True  # Автоматический запуск бота при старте сервера


# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'users.telegram_auth.TelegramAuthBackend',  # Если захотите кастомный бэкенд
]