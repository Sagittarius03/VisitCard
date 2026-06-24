from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, TelegramMessage, TelegramSession


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'get_display_name', 'first_name', 
        'last_name', 'is_active', 'total_messages', 'last_activity'
    ]
    list_filter = ['is_active', 'is_blocked', 'is_bot', 'language_code']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = [
        'telegram_id', 'first_activity', 'last_activity', 
        'total_messages', 'get_display_name'
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'telegram_id', 'get_display_name', 'username',
                'first_name', 'last_name', 'phone_number'
            )
        }),
        ('Данные Telegram', {
            'fields': ('language_code', 'is_bot')
        }),
        ('Статусы', {
            'fields': ('is_active', 'is_blocked')
        }),
        ('Статистика', {
            'fields': ('total_messages', 'first_activity', 'last_activity')
        }),
        ('Связи', {
            'fields': ('user',)
        }),
        ('Дополнительно', {
            'fields': ('custom_data',),
            'classes': ('collapse',)
        })
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Отображаемое имя'


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'message_type', 'is_command', 
        'is_incoming', 'short_content', 'created_at'
    ]
    list_filter = ['message_type', 'is_command', 'is_incoming', 'created_at']
    search_fields = ['content', 'user__username', 'user__first_name']
    readonly_fields = ['created_at', 'raw_data']
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'message_id', 'chat_id', 'message_type')
        }),
        ('Содержимое', {
            'fields': ('content', 'is_command', 'command_name', 'replied_to')
        }),
        ('Направление', {
            'fields': ('is_incoming',)
        }),
        ('Данные', {
            'fields': ('raw_data', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def short_content(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return 'Нет текста'
    short_content.short_description = 'Содержимое'


@admin.register(TelegramSession)
class TelegramSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'state', 'updated_at']
    list_filter = ['state', 'updated_at']
    search_fields = ['user__username', 'user__first_name', 'state']