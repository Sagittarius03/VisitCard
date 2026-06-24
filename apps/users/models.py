from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator
from filer.fields.image import FilerImageField  # Добавляем импорт filer


class User(AbstractUser):
    """
    Расширенная модель пользователя
    """
    # ==================== ОСНОВНЫЕ ПОЛЯ ====================
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Логин"
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        error_messages={
            'unique': "Пользователь с таким email уже существует.",
        }
    )
    
    phone = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message="Введите корректный номер телефона (например, +77001234567)"
            )
        ]
    )
    
    # ==================== TELEGRAM СВЯЗЬ ====================
    telegram_user = models.ForeignKey(
        'telega.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='django_users',
        verbose_name="Telegram пользователь",
        help_text="Связь с пользователем в Telegram"
    )
    
    telegram_verified = models.BooleanField(
        default=False,
        verbose_name="Telegram верифицирован",
        help_text="Подтверждено, что пользователь владеет этим Telegram"
    )
    
    # ==================== ЛИЧНЫЕ ДАННЫЕ ====================
    # Используем FilerImageField вместо стандартного ImageField
    avatar = FilerImageField(
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_avatar',
        verbose_name="Аватар",
        help_text="Загрузите изображение для аватара"
    )
    
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[
            ('male', 'Мужской'),
            ('female', 'Женский'),
        ],
        verbose_name="Пол"
    )
    
    # ==================== СОЦИАЛЬНЫЕ СЕТИ ====================
    vk_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="VK",
        help_text="Ссылка на профиль VK"
    )
    
    instagram_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Instagram",
        help_text="Ссылка на профиль Instagram"
    )
    
    # ==================== ГЕОГРАФИЯ ====================
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Страна"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город"
    )
    
    # ==================== IP АВТОРИЗАЦИИ ====================
    auth_ips = models.JSONField(
        default=list,
        blank=True,
        verbose_name="IP авторизации",
        help_text="Список IP-адресов с датами входа (максимум 10)"
    )
    
    # ==================== РОЛЬ И СТАТУС ====================
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name="Роль"
    )
    
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('blocked', 'Заблокирован'),
        ('pending', 'Ожидает подтверждения'),
        ('deleted', 'Удален'),
        ('suspended', 'Приостановлен'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    # ==================== ВРЕМЕННЫЕ МЕТКИ ====================
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата регистрации"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    last_seen = models.DateTimeField(
        default=timezone.now,
        verbose_name="Последний визит"
    )
    
    # ==================== НАСТРОЙКИ ====================
    timezone = models.CharField(
        max_length=50,
        default='Asia/Almaty',
        verbose_name="Часовой пояс",
        help_text="Часовой пояс пользователя"
    )
    
    # ==================== ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ ====================
    accepted_privacy_policy_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата согласия на политику",
        help_text="Когда пользователь принял условия политики конфиденциальности"
    )
    
    privacy_policy_version = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Версия политики",
        help_text="Версия документа, с которым согласился пользователь"
    )
    
    warnings_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество предупреждений"
    )
    # ==================== МЕТАДАННЫЕ ====================
    meta_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Дополнительные данные"
    )
    
    # ==================== ⭐ ИСПРАВЛЕНИЕ КОНФЛИКТА ====================
    # Явно указываем related_name для групп и разрешений
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['username']),
            models.Index(fields=['status']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

    def get_full_name(self):
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_short_name(self):
        """Короткое имя"""
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name[:1]}."
            return self.first_name
        return self.username

    def has_telegram(self):
        """Проверка, связан ли пользователь с Telegram"""
        return self.telegram_user is not None

    def fill_from_telegram(self, telegram_user_data):
        """
        Заполнить имя и фамилию из данных Telegram, если они не указаны
        
        Args:
            telegram_user_data: объект TelegramUser или словарь с полями
                first_name, last_name, username
        """
        if not telegram_user_data:
            return
        
        # Получаем данные из объекта или словаря
        if hasattr(telegram_user_data, 'first_name'):
            tg_first = telegram_user_data.first_name
            tg_last = telegram_user_data.last_name
            tg_username = telegram_user_data.username
        else:
            tg_first = telegram_user_data.get('first_name')
            tg_last = telegram_user_data.get('last_name')
            tg_username = telegram_user_data.get('username')
        
        # Заполняем имя, если не указано
        if not self.first_name and tg_first:
            self.first_name = tg_first
        
        # Заполняем фамилию, если не указана
        if not self.last_name and tg_last:
            self.last_name = tg_last
        
        # Если имя все еще пустое, используем username
        if not self.first_name and tg_username:
            self.first_name = tg_username
        
        # Сохраняем изменения
        if self.pk:
            self.save(update_fields=['first_name', 'last_name'])

    def add_auth_ip(self, ip_address, user_agent=None):
        """
        Добавить IP авторизации с датой
        Сохраняет последние 10 записей
        """
        if not ip_address:
            return
        
        current_ips = self.auth_ips if isinstance(self.auth_ips, list) else []
        
        # Проверяем, есть ли уже такой IP
        for entry in current_ips:
            if entry.get('ip') == ip_address:
                entry['date'] = timezone.now().isoformat()
                if user_agent:
                    entry['user_agent'] = user_agent
                self.auth_ips = current_ips
                self.save(update_fields=['auth_ips'])
                return
        
        # Добавляем новый IP
        new_entry = {
            'ip': ip_address,
            'date': timezone.now().isoformat(),
        }
        if user_agent:
            new_entry['user_agent'] = user_agent
        
        current_ips.append(new_entry)
        
        # Оставляем только последние 10
        if len(current_ips) > 10:
            current_ips = current_ips[-10:]
        
        self.auth_ips = current_ips
        self.save(update_fields=['auth_ips'])

    def get_last_ips(self, limit=10):
        """Получить последние N IP-адресов"""
        ips = self.auth_ips if isinstance(self.auth_ips, list) else []
        return ips[-limit:] if ips else []

    def is_blocked(self):
        """Проверка, заблокирован ли пользователь"""
        return self.status == 'blocked'

    def block(self):
        """Заблокировать пользователя"""
        self.status = 'blocked'
        self.save(update_fields=['status'])

    def unblock(self):
        """Разблокировать пользователя"""
        self.status = 'active'
        self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        """Переопределение save для автоматической установки username из email"""
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        if not self.username and self.phone:
            self.username = self.phone
        super().save(*args, **kwargs)

    # def clean(self):
    #     super().clean()
    #     if self.phone:
    #         # Валидация только если поле заполнено
    #         from django.core.validators import validate_regex
    #         validate_regex(
    #             r'^\+?[0-9]{10,15}$',
    #             message="Введите корректный номер телефона (например, +77001234567)"
    #         )(self.phone)

class Blacklist(models.Model):
    """
    Черный список для бана пользователей и IP
    """
    BLOCK_TYPE_CHOICES = [
        ('user', 'Пользователь'),
        ('ip', 'IP-адрес'),
        ('email', 'Email'),
    ]
    
    block_type = models.CharField(
        max_length=10,
        choices=BLOCK_TYPE_CHOICES,
        verbose_name="Тип блокировки"
    )
    
    value = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Значение",
        help_text="ID пользователя, IP-адрес или Email"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='blacklist_entries',
        verbose_name="Пользователь"
    )
    
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Причина"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Истекает",
        help_text="Если указано - временная блокировка"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_blacklist_entries',
        verbose_name="Кем добавлен"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Действует ли блокировка"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Уже есть
        null=True,
        blank=True,
        related_name='created_blacklist_entries',
        verbose_name="Кем добавлен"
    )
    
    class Meta:
        db_table = 'blacklist'
        verbose_name = 'Черный список'
        verbose_name_plural = 'Черный список'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['block_type', 'value']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_block_type_display()}: {self.value}"

    def is_expired(self):
        """Проверка, истекла ли блокировка"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_active_block(self):
        """Проверка, активна ли блокировка"""
        return self.is_active and not self.is_expired()

    @classmethod
    def is_blocked(cls, block_type, value):
        """Проверить, заблокировано ли значение"""
        try:
            entry = cls.objects.get(
                block_type=block_type,
                value=value,
                is_active=True
            )
            return not entry.is_expired()
        except cls.DoesNotExist:
            return False

    @classmethod
    def block_user(cls, user, reason=None, expires_at=None, created_by=None):
        """Заблокировать пользователя"""
        entry, created = cls.objects.get_or_create(
            block_type='user',
            value=str(user.id),
            defaults={
                'user': user,
                'reason': reason,
                'expires_at': expires_at,
                'created_by': created_by,
                'is_active': True,
            }
        )
        if not created:
            entry.is_active = True
            entry.reason = reason or entry.reason
            entry.expires_at = expires_at or entry.expires_at
            entry.save()
        
        user.status = 'blocked'
        user.save(update_fields=['status'])
        
        return entry

    @classmethod
    def block_ip(cls, ip_address, reason=None, expires_at=None, created_by=None):
        """Заблокировать IP-адрес"""
        entry, created = cls.objects.get_or_create(
            block_type='ip',
            value=ip_address,
            defaults={
                'reason': reason,
                'expires_at': expires_at,
                'created_by': created_by,
                'is_active': True,
            }
        )
        if not created:
            entry.is_active = True
            entry.reason = reason or entry.reason
            entry.expires_at = expires_at or entry.expires_at
            entry.save()
        
        return entry

    @classmethod
    def unblock(cls, block_type, value):
        """Разблокировать"""
        try:
            entry = cls.objects.get(block_type=block_type, value=value)
            entry.is_active = False
            entry.save()
            
            if block_type == 'user':
                try:
                    user = User.objects.get(id=int(value))
                    user.status = 'active'
                    user.save(update_fields=['status'])
                except User.DoesNotExist:
                    pass
            
            return True
        except cls.DoesNotExist:
            return False
    
    
class UserWarning(models.Model):
    """
    Модель для хранения предупреждений пользователей
    """
    WARNING_TYPES = [
        ('spam', 'Спам'),
        ('insult', 'Оскорбление'),
        ('flood', 'Флуд'),
        ('rule_violation', 'Нарушение правил'),
        ('advertising', 'Реклама'),
        ('other', 'Другое'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # или SET_NULL, в зависимости от логики
        related_name='warnings',
        verbose_name="Пользователь"
    )
    warning_type = models.CharField(
        max_length=20,
        choices=WARNING_TYPES,
        default='other',
        verbose_name="Тип предупреждения"
    )
    
    reason = models.TextField(
        verbose_name="Причина",
        help_text="Подробное описание причины предупреждения"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_warnings',
        verbose_name="Кем выдано"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата выдачи"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Истекает",
        help_text="Если указано - предупреждение временное"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Действует ли предупреждение"
    )
    
    class Meta:
        db_table = 'user_warnings'
        verbose_name = 'Предупреждение'
        verbose_name_plural = 'Предупреждения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_warning_type_display()} ({self.created_at.strftime('%d.%m.%Y')})"
    
    def is_expired(self):
        """Проверка, истекло ли предупреждение"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
class UserIPHistory(models.Model):
    """
    Модель для хранения истории IP-адресов пользователей
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # или SET_NULL
        related_name='ip_history',
        verbose_name="Пользователь"
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name="IP-адрес"
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Местоположение",
        help_text="Страна, город (определяется по IP)"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="Информация о браузере и устройстве"
    )
    
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время входа"
    )
    
    is_successful = models.BooleanField(
        default=True,
        verbose_name="Успешный вход",
        help_text="Был ли вход успешным"
    )
    
    class Meta:
        db_table = 'user_ip_history'
        verbose_name = 'История IP'
        verbose_name_plural = 'История IP'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'login_time']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.login_time.strftime('%d.%m.%Y %H:%M')})"