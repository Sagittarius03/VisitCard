from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import User, Blacklist, UserWarning, UserIPHistory


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'id', 'username', 'email', 'phone_display', 
        'telegram_status', 'warnings_count_display', 'role', 'status', 'date_joined'
    ]
    list_filter = ['status', 'role', 'telegram_verified', 'date_joined', 'warnings_count']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'updated_at', 'auth_ips', 'phone_display', 'telegram_status', 'warnings_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'username', 'email', 'phone', 'password',
                'first_name', 'last_name', 'gender', 'avatar'
            )
        }),
        ('Telegram', {
            'fields': ('telegram_user', 'telegram_verified')
        }),
        ('Социальные сети', {
            'fields': ('vk_url', 'instagram_url')
        }),
        ('География', {
            'fields': ('country', 'city')
        }),
        ('Права', {
            'fields': ('role', 'status', 'groups', 'user_permissions')
        }),
        ('Статистика', {
            'fields': ('auth_ips', 'warnings_count', 'date_joined', 'updated_at', 'last_seen')
        }),
        ('Политика конфиденциальности', {
            'fields': ('accepted_privacy_policy_at', 'privacy_policy_version')
        }),
        ('Дополнительно', {
            'fields': ('meta_data', 'timezone'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['ban_users', 'unban_users', 'mute_users', 'add_warning', 'ban_by_ip']
    
    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        return list(readonly) + ['date_joined', 'updated_at', 'auth_ips']
    
    def phone_display(self, obj):
        if obj.phone:
            return format_html(
                '<span class="phone-display">{}</span>',
                obj.phone
            )
        return '-'
    phone_display.short_description = 'Телефон'
    
    def telegram_status(self, obj):
        if obj.telegram_user:
            status = '✅ Активен' if obj.telegram_verified else '⏳ Не верифицирован'
            return format_html(
                '<span class="telegram-user-link active">{}</span>',
                status
            )
        return '❌ Не связан'
    telegram_status.short_description = 'Telegram'
    
    def warnings_count_display(self, obj):
        if obj.warnings_count > 0:
            color = 'orange' if obj.warnings_count < 3 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">⚠️ {}</span>',
                color,
                obj.warnings_count
            )
        return '✅ Нет'
    warnings_count_display.short_description = 'Предупреждения'
    
    # Действия для админки
    
    def ban_users(self, request, queryset):
        """Забанить выбранных пользователей"""
        count = 0
        for user in queryset:
            if user.status != 'blocked':
                user.block()
                count += 1
        self.message_user(request, f'Забанено {count} пользователей.', messages.SUCCESS)
    ban_users.short_description = '🔨 Забанить выбранных пользователей'
    
    def unban_users(self, request, queryset):
        """Разбанить выбранных пользователей"""
        count = 0
        for user in queryset:
            if user.status == 'blocked':
                user.unblock()
                count += 1
        self.message_user(request, f'Разбанено {count} пользователей.', messages.SUCCESS)
    unban_users.short_description = '🔓 Разбанить выбранных пользователей'
    
    def mute_users(self, request, queryset):
        """Замутить выбранных пользователей (временно заблокировать)"""
        duration = request.GET.get('duration', '1')
        days = int(duration) if duration.isdigit() else 1
        
        count = 0
        for user in queryset:
            if user.status != 'blocked':
                expires_at = timezone.now() + timezone.timedelta(days=days)
                Blacklist.block_user(
                    user=user,
                    reason=f'Мут на {days} дней',
                    expires_at=expires_at,
                    created_by=request.user
                )
                count += 1
        self.message_user(
            request, 
            f'Замучено {count} пользователей на {days} дней.', 
            messages.SUCCESS
        )
    mute_users.short_description = '🔇 Замутить выбранных пользователей'
    
    def add_warning(self, request, queryset):
        """Добавить предупреждение выбранным пользователям"""
        # Перенаправляем на страницу добавления предупреждения
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return redirect(f'{reverse("admin:users_userwarning_add")}?users={",".join(selected)}')
    add_warning.short_description = '⚠️ Добавить предупреждение'
    
    def ban_by_ip(self, request, queryset):
        """Забанить по IP выбранных пользователей"""
        count = 0
        for user in queryset:
            # Получаем последний IP пользователя
            last_ip = user.ip_history.filter(is_successful=True).first()
            if last_ip:
                Blacklist.block_ip(
                    ip_address=last_ip.ip_address,
                    reason=f'Бан по IP от пользователя {user.username}',
                    created_by=request.user
                )
                count += 1
            else:
                self.message_user(
                    request,
                    f'Для пользователя {user.username} нет IP в истории.',
                    messages.WARNING
                )
        if count > 0:
            self.message_user(
                request,
                f'Забанено по IP {count} пользователей.',
                messages.SUCCESS
            )
    ban_by_ip.short_description = '🚫 Забанить по IP выбранных пользователей'


@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'warning_type', 'reason_short', 'created_by', 'created_at', 'is_active']
    list_filter = ['warning_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'reason']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'warning_type', 'reason')
        }),
        ('Кем выдано', {
            'fields': ('created_by',)
        }),
        ('Время', {
            'fields': ('expires_at', 'is_active', 'created_at')
        }),
    )
    
    def reason_short(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Причина'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
        # Обновляем количество предупреждений у пользователя
        user = obj.user
        user.warnings_count = user.warnings.filter(is_active=True).count()
        user.save(update_fields=['warnings_count'])
    
    def delete_model(self, request, obj):
        user = obj.user
        super().delete_model(request, obj)
        user.warnings_count = user.warnings.filter(is_active=True).count()
        user.save(update_fields=['warnings_count'])


@admin.register(UserIPHistory)
class UserIPHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ip_address', 'location', 'login_time', 'is_successful']
    list_filter = ['is_successful', 'login_time']
    search_fields = ['user__username', 'user__email', 'ip_address', 'location']
    readonly_fields = ['user', 'ip_address', 'location', 'user_agent', 'login_time', 'is_successful']
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'ip_address', 'location')
        }),
        ('Информация', {
            'fields': ('user_agent', 'login_time', 'is_successful')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ['id', 'block_type', 'value', 'user', 'reason', 'is_active', 'expires_at', 'created_at']
    list_filter = ['block_type', 'is_active', 'created_at']
    search_fields = ['value', 'user__username', 'user__email', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основное', {
            'fields': ('block_type', 'value', 'user')
        }),
        ('Причина', {
            'fields': ('reason',)
        }),
        ('Время', {
            'fields': ('expires_at', 'is_active')
        }),
        ('Кем добавлено', {
            'fields': ('created_by',)
        }),
        ('Метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['unblock_selected']
    
    def unblock_selected(self, request, queryset):
        """Разблокировать выбранные записи"""
        count = 0
        for entry in queryset:
            if entry.is_active:
                entry.is_active = False
                entry.save()
                count += 1
                
                if entry.block_type == 'user' and entry.user:
                    entry.user.unblock()
        self.message_user(request, f'Разблокировано {count} записей.', messages.SUCCESS)
    unblock_selected.short_description = '🔓 Разблокировать выбранные'