from typing import Optional, Dict, Any
from telebot.types import Message, User
from django.utils import timezone
from telega.models import TelegramUser, TelegramMessage


def get_or_create_telegram_user(telegram_user: User, **kwargs) -> TelegramUser:
    """
    Получить или создать пользователя в БД
    """
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_user.id,
        defaults={
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name,
            'language_code': telegram_user.language_code,
            'is_bot': telegram_user.is_bot,
            'first_activity': timezone.now(),
            'last_activity': timezone.now(),
        }
    )
    
    # Если пользователь уже существует, обновляем данные
    if not created:
        updated = False
        
        # Обновляем поля, если они изменились
        if user.username != telegram_user.username:
            user.username = telegram_user.username
            updated = True
        if user.first_name != telegram_user.first_name:
            user.first_name = telegram_user.first_name
            updated = True
        if user.last_name != telegram_user.last_name:
            user.last_name = telegram_user.last_name
            updated = True
        if user.language_code != telegram_user.language_code:
            user.language_code = telegram_user.language_code
            updated = True
            
        # Если пользователь ранее был заблокирован, разблокируем
        if user.is_blocked:
            user.is_blocked = False
            updated = True
            
        # Обновляем время последней активности
        user.last_activity = timezone.now()
        user.total_messages += 1
        updated = True
        
        if updated:
            user.save()
    
    return user


def save_message(
    message: Message,
    is_incoming: bool = True,
    is_command: bool = False,
    command_name: str = None,
    message_type: str = 'text',
    content: str = None,
    raw_data: Dict = None
) -> Optional[TelegramMessage]:
    """
    Сохранить сообщение в БД
    """
    try:
        # Получаем пользователя
        telegram_user = TelegramUser.objects.filter(
            telegram_id=message.from_user.id
        ).first()
        
        if not telegram_user:
            return None
        
        # Определяем тип сообщения
        if message_type == 'text' and content is None:
            content = message.text or ''
        
        # Определяем ID чата
        chat_id = message.chat.id if message.chat else None
        
        # Определяем ID сообщения
        message_id = message.message_id if hasattr(message, 'message_id') else None
        
        # Сохраняем сообщение
        msg = TelegramMessage.objects.create(
            user=telegram_user,
            message_id=message_id,
            chat_id=chat_id,
            message_type=message_type,
            content=content or '',
            is_incoming=is_incoming,
            is_command=is_command,
            command_name=command_name,
            raw_data=raw_data or {},
        )
        
        # Обновляем последний ID сообщения у пользователя
        telegram_user.last_message_id = message_id
        telegram_user.save(update_fields=['last_message_id'])
        
        return msg
        
    except Exception as e:
        print(f"Ошибка сохранения сообщения: {e}")
        return None


def get_user_state(user_id: int) -> Dict[str, Any]:
    """
    Получить состояние пользователя
    """
    from telega.models import TelegramSession
    
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=user_id)
        session, _ = TelegramSession.objects.get_or_create(user=telegram_user)
        return {
            'state': session.state,
            'data': session.data
        }
    except TelegramUser.DoesNotExist:
        return {'state': None, 'data': {}}


def set_user_state(user_id: int, state: str, data: Dict = None):
    """
    Установить состояние пользователя
    """
    from telega.models import TelegramSession
    
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=user_id)
        session, _ = TelegramSession.objects.get_or_create(user=telegram_user)
        session.state = state
        if data is not None:
            session.data.update(data)
        session.save()
        return True
    except TelegramUser.DoesNotExist:
        return False


def clear_user_state(user_id: int):
    """
    Очистить состояние пользователя
    """
    from telega.models import TelegramSession
    
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=user_id)
        TelegramSession.objects.filter(user=telegram_user).delete()
        return True
    except TelegramUser.DoesNotExist:
        return False


def get_user_by_id(user_id: int) -> Optional[TelegramUser]:
    """
    Получить пользователя по Telegram ID
    """
    try:
        return TelegramUser.objects.get(telegram_id=user_id)
    except TelegramUser.DoesNotExist:
        return None


def is_user_exists(user_id: int) -> bool:
    """
    Проверить, существует ли пользователь в БД
    """
    return TelegramUser.objects.filter(telegram_id=user_id).exists()

def sync_user_from_telegram(telegram_user):
    """
    Синхронизировать Django пользователя с данными из Telegram
    
    Args:
        telegram_user: объект TelegramUser
    
    Returns:
        User: Django пользователь
    """
    from apps.users.models import User
    
    # Ищем Django пользователя
    try:
        django_user = User.objects.get(telegram_user=telegram_user)
        
        # Обновляем имя/фамилию, если они изменились
        updated = False
        if not django_user.first_name and telegram_user.first_name:
            django_user.first_name = telegram_user.first_name
            updated = True
        if not django_user.last_name and telegram_user.last_name:
            django_user.last_name = telegram_user.last_name
            updated = True
        
        if updated:
            django_user.save(update_fields=['first_name', 'last_name'])
        
        return django_user
        
    except User.DoesNotExist:
        # Создаем нового пользователя
        django_user = User.objects.create_user(
            username=f"tg_{telegram_user.telegram_id}",
            email=f"{telegram_user.telegram_id}@telegram.user",
            first_name=telegram_user.first_name or '',
            last_name=telegram_user.last_name or '',
            telegram_user=telegram_user,
            telegram_verified=True,
            status='active'
        )
        
        # Заполняем имя/фамилию из Telegram
        django_user.fill_from_telegram(telegram_user)
        
        return django_user