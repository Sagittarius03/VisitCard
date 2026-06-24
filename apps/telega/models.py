from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TelegramUser(models.Model):
    """
    Модель для хранения пользователей Telegram
    """
    # Основные данные от Telegram
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Номер телефона"
    )
    language_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Код языка",
        help_text="Язык пользователя (например, ru, en)"
    )
    is_bot = models.BooleanField(
        default=False,
        verbose_name="Бот",
        help_text="Является ли пользователь ботом"
    )
    
    # Связь с пользователем Django (если есть)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='telegram_users',
        verbose_name="Пользователь Django"
    )
    
    # Статусы и состояния
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Может ли пользователь взаимодействовать с ботом"
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован",
        help_text="Заблокировал ли пользователь бота"
    )
    
    # Дополнительные метаданные
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя активность"
    )
    first_activity = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Первая активность"
    )
    last_message_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="ID последнего сообщения"
    )
    total_messages = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего сообщений"
    )
    
    # Кастомные данные
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Дополнительные данные",
        help_text="Любые дополнительные данные в формате JSON"
    )
    
    class Meta:
        db_table = 'telegram_users'
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['username']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        if self.username:
            return f"@{self.username} ({self.telegram_id})"
        return f"{self.first_name or 'Unknown'} {self.last_name or ''} - {self.telegram_id}"

    def get_full_name(self):
        """Получить полное имя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or f"User {self.telegram_id}"

    def get_display_name(self):
        """Получить имя для отображения"""
        if self.username:
            return f"@{self.username}"
        return self.get_full_name()


class TelegramMessage(models.Model):
    """
    Модель для хранения истории сообщений
    """
    # Связь с пользователем
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Пользователь"
    )
    
    # Данные сообщения
    message_id = models.BigIntegerField(
        verbose_name="ID сообщения",
        help_text="ID сообщения в Telegram"
    )
    chat_id = models.BigIntegerField(
        verbose_name="ID чата",
        help_text="ID чата, где было отправлено сообщение"
    )
    message_type = models.CharField(
        max_length=50,
        default='text',
        verbose_name="Тип сообщения",
        choices=[
            ('text', 'Текст'),
            ('photo', 'Фото'),
            ('video', 'Видео'),
            ('document', 'Документ'),
            ('voice', 'Голосовое'),
            ('sticker', 'Стикер'),
            ('callback_query', 'Callback'),
            ('inline_query', 'Inline'),
            ('command', 'Команда'),
            ('unknown', 'Неизвестно'),
        ]
    )
    
    # Содержимое
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name="Содержимое",
        help_text="Текст сообщения или описание медиа"
    )
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Сырые данные",
        help_text="Полные данные сообщения от Telegram"
    )
    
    # Метаданные
    is_incoming = models.BooleanField(
        default=True,
        verbose_name="Входящее",
        help_text="True - пользователь -> бот, False - бот -> пользователь"
    )
    is_command = models.BooleanField(
        default=False,
        verbose_name="Команда",
        help_text="Является ли сообщение командой"
    )
    command_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Название команды"
    )
    
    # Ответы
    replied_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Ответ на"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        db_table = 'telegram_messages'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['chat_id', 'message_id']),
            models.Index(fields=['is_command']),
        ]
        unique_together = [['chat_id', 'message_id']]

    def __str__(self):
        if self.is_incoming:
            direction = "📥"
        else:
            direction = "📤"
        return f"{direction} {self.user} - {self.content[:50] if self.content else 'No text'}"


class TelegramSession(models.Model):
    """
    Модель для хранения сессий/состояний пользователей
    (Для FSM - Finite State Machine)
    """
    user = models.OneToOneField(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='session',
        verbose_name="Пользователь"
    )
    
    state = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Состояние",
        help_text="Текущее состояние диалога"
    )
    
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Данные сессии",
        help_text="Временные данные состояния"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено"
    )
    
    class Meta:
        db_table = 'telegram_sessions'
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"Сессия {self.user} - {self.state or 'без состояния'}"