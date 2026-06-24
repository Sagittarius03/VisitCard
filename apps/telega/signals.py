from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import TelegramUser

User = get_user_model()


@receiver(post_save, sender=TelegramUser)
def handle_telegram_user_link(sender, instance, created, **kwargs):
    """
    При создании или обновлении TelegramUser проверяем дубли
    """
    if not instance.user:
        return
    
    # Проверяем, есть ли другие TelegramUser с таким же пользователем
    duplicates = TelegramUser.objects.filter(
        user=instance.user
    ).exclude(id=instance.id)
    
    # Удаляем дубли, перенося сообщения и сессии
    for dup in duplicates:
        # Переносим сообщения
        dup.messages.update(user=instance)
        # Переносим сессию
        if hasattr(dup, 'session'):
            dup.session.user = instance
            dup.session.save()
        # Удаляем дубль
        dup.delete()