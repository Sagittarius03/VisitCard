from .core import bot
from .utils import (
    get_or_create_telegram_user,
    save_message,
    is_user_exists,
    get_user_by_id
)
from telebot.types import Message
from users.models import User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def start_command(message: Message):
    """
    Обработчик команды /start
    """
    try:
        # Получаем или создаем Telegram пользователя
        telegram_user = get_or_create_telegram_user(message.from_user)
        
        # Сохраняем команду
        save_message(
            message=message,
            is_incoming=True,
            is_command=True,
            command_name='start',
            message_type='command',
            content='/start'
        )
        
        # Ищем Django пользователя по Telegram ID
        try:
            django_user = User.objects.get(telegram_user=telegram_user)
        except User.DoesNotExist:
            # Создаем нового Django пользователя
            django_user = User.objects.create_user(
                username=f"tg_{telegram_user.telegram_id}",
                email=f"{telegram_user.telegram_id}@telegram.user",
                first_name=telegram_user.first_name or '',
                last_name=telegram_user.last_name or '',
                telegram_user=telegram_user,
                telegram_verified=True,
                status='active'
            )
            
            # Заполняем имя/фамилию из Telegram, если не указаны
            django_user.fill_from_telegram(telegram_user)
            
            welcome_message = (
                "👋 Здравствуйте!\n\n"
                "Я бот-помощник. Чтобы узнать доступные команды, используйте /help.\n"
                "Вы можете отправить любое сообщение, и оно будет сохранено."
            )
            
            bot.send_message(
                message.chat.id,
                welcome_message,
                parse_mode='HTML'
            )
        else:
            # Пользователь уже существует
            # Обновляем данные из Telegram, если они изменились
            if django_user.first_name != telegram_user.first_name or \
               django_user.last_name != telegram_user.last_name:
                django_user.fill_from_telegram(telegram_user)
            
            # Заглушка - ничего не делаем
            logger.info(f"Пользователь {telegram_user.telegram_id} уже существует")
            
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка. Попробуйте позже."
        )

@bot.message_handler(commands=['help'])
def help_command(message: Message):
    """
    Обработчик команды /help
    """
    try:
        # Получаем пользователя
        telegram_user = get_or_create_telegram_user(message.from_user)
        
        # Сохраняем команду
        save_message(
            message=message,
            is_incoming=True,
            is_command=True,
            command_name='help',
            message_type='command',
            content='/help'
        )
        
        help_text = (
            "📚 <b>Доступные команды:</b>\n\n"
            "🔹 /start - Приветствие и регистрация\n"
            "🔹 /help - Показать эту справку\n"
            "🔹 /profile - Моя визитка\n"
            "🔹 /edit - Редактировать визитку\n"
            "🔹 /contacts - Мои контакты\n"
            "🔹 /settings - Настройки\n\n"
            "💡 Просто отправьте любое сообщение, и я отвечу!"
        )
        
        bot.send_message(
            message.chat.id,
            help_text,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в /help: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка."
        )


@bot.message_handler(commands=['profile'])
def profile_command(message: Message):
    """
    Обработчик команды /profile - показывает визитку
    """
    try:
        telegram_user = get_or_create_telegram_user(message.from_user)
        
        save_message(
            message=message,
            is_incoming=True,
            is_command=True,
            command_name='profile',
            message_type='command',
            content='/profile'
        )
        
        profile_text = (
            f"👤 <b>Ваш профиль</b>\n\n"
            f"🔹 <b>Имя:</b> {telegram_user.first_name or 'Не указано'}\n"
            f"🔹 <b>Фамилия:</b> {telegram_user.last_name or 'Не указана'}\n"
            f"🔹 <b>Username:</b> @{telegram_user.username or 'Не указан'}\n"
            f"🔹 <b>ID:</b> {telegram_user.telegram_id}\n"
            f"🔹 <b>Язык:</b> {telegram_user.language_code or 'Не указан'}\n"
            f"🔹 <b>Сообщений:</b> {telegram_user.total_messages}\n"
            f"🔹 <b>Активен с:</b> {telegram_user.first_activity.strftime('%d.%m.%Y %H:%M')}\n"
        )
        
        bot.send_message(
            message.chat.id,
            profile_text,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в /profile: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка."
        )


@bot.message_handler(commands=['stats'])
def stats_command(message: Message):
    """
    Команда /stats - показывает статистику (можно сделать админской)
    """
    try:
        # Проверка, является ли пользователь администратором
        admin_chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', None)
        if str(message.from_user.id) != str(admin_chat_id):
            bot.send_message(
                message.chat.id,
                "⛔ У вас нет прав на эту команду."
            )
            return
        
        save_message(
            message=message,
            is_incoming=True,
            is_command=True,
            command_name='stats',
            message_type='command',
            content='/stats'
        )
        
        from ..models import TelegramUser, TelegramMessage
        
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(
            is_active=True, 
            is_blocked=False
        ).count()
        total_messages = TelegramMessage.objects.filter(
            is_incoming=True
        ).count()
        
        stats_text = (
            f"📊 <b>Статистика бота</b>\n\n"
            f"👥 <b>Всего пользователей:</b> {total_users}\n"
            f"✅ <b>Активных:</b> {active_users}\n"
            f"💬 <b>Всего сообщений:</b> {total_messages}\n"
        )
        
        bot.send_message(
            message.chat.id,
            stats_text,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в /stats: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка."
        )


@bot.message_handler(func=lambda message: True)
def all_messages_handler(message: Message):
    """
    Обработчик всех остальных сообщений
    Сохраняет все входящие сообщения в БД
    """
    try:
        # Получаем или создаем пользователя
        telegram_user = get_or_create_telegram_user(message.from_user)
        
        # Определяем тип сообщения
        message_type = 'text'
        content = message.text or ''
        
        if message.photo:
            message_type = 'photo'
            content = f"[Фото] {message.caption or ''}"
        elif message.video:
            message_type = 'video'
            content = f"[Видео] {message.caption or ''}"
        elif message.document:
            message_type = 'document'
            content = f"[Документ] {message.document.file_name or ''}"
        elif message.voice:
            message_type = 'voice'
            content = "[Голосовое сообщение]"
        elif message.sticker:
            message_type = 'sticker'
            content = f"[Стикер] {message.sticker.emoji or ''}"
        elif message.location:
            message_type = 'location'
            content = f"[Локация] {message.location.latitude}, {message.location.longitude}"
        
        # Сохраняем сообщение
        save_message(
            message=message,
            is_incoming=True,
            is_command=False,
            command_name=None,
            message_type=message_type,
            content=content,
            raw_data=message.json if hasattr(message, 'json') else {}
        )
        
        # Отправляем ответ для не-команд
        # Если текст не начинается с "/", отвечаем
        if not message.text or not message.text.startswith('/'):
            response_text = (
                "💬 <b>Сообщение получено!</b>\n\n"
                "🔄 Ваши данные сохранены.\n"
                "ℹ️ Используйте /help для списка команд."
            )
            
            bot.reply_to(
                message,
                response_text,
                parse_mode='HTML'
            )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике сообщений: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при обработке вашего сообщения."
        )