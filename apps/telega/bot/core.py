from django.conf import settings
import telebot

token = getattr(settings, "TELEGRAM_BOT_TOKEN")
if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN не задан в settings.py")

bot = telebot.TeleBot(token, 
        parse_mode='HTML',            # Разметка текста
        threaded=True,                # Многопоточность
        skip_pending=True,            # Пропускать сообщения, когда офлайн
        num_threads = 2,              # Покотов для обработки
        disable_notification = False, # Уведомление пользователя о сообщении
        validate_token = False,       # Проверить токен 
        
)


