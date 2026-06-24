import os
import threading

from django.apps import AppConfig

from utils.text_format import printf


class TelegaConfig(AppConfig):
    name = 'telega'
    _bot_started = False

    def ready(self):
        import telega.signals  # noqa
        
        if os.environ.get('RUN_MAIN', None) != 'true':
            printf("<info>⏭️ Пропускаем запуск бота в основном процессе</info>")
            return
        
        # Защита от двойного запуска
        if self._bot_started:
            return
        self._bot_started = True
        
        def run_bot():
            try:
                from telega.bot.core import bot
                printf("<success>🤖 Telegram бот запущен!</success>")
                bot.infinity_polling()
            except Exception as e:
                printf(f"<error>❌ Ошибка бота: {e}</error>")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        printf("<info>📦 Telegram бот инициализирован в фоновом потоке</info>")