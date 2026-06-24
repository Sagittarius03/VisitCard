from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from telega.models import TelegramUser, TelegramMessage, TelegramSession
from users.models import Blacklist, UserIPHistory

User = get_user_model()

# Флаг для предотвращения рекурсии
_merging_in_progress = False


def merge_telegram_user_data(main_tg, dup_tg):
    """Объединяет данные из дубля в основной объект TelegramUser"""
    fields_merged = 0
    
    fields_to_merge = [
        ('username', 'username'),
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('phone_number', 'phone_number'),
        ('language_code', 'language_code'),
    ]
    
    for main_field, dup_field in fields_to_merge:
        main_value = getattr(main_tg, main_field, None)
        dup_value = getattr(dup_tg, dup_field, None)
        
        if (main_value is None or main_value == '') and dup_value:
            setattr(main_tg, main_field, dup_value)
            fields_merged += 1
            print(f"  - Перенесено {main_field}: '{dup_value}'")
    
    if dup_tg.total_messages > 0:
        main_tg.total_messages += dup_tg.total_messages
        fields_merged += 1
        print(f"  - Суммировано сообщений: +{dup_tg.total_messages}")
    
    if dup_tg.last_activity and (not main_tg.last_activity or dup_tg.last_activity > main_tg.last_activity):
        main_tg.last_activity = dup_tg.last_activity
        fields_merged += 1
        print(f"  - Обновлена последняя активность: {dup_tg.last_activity}")
    
    if dup_tg.first_activity and (not main_tg.first_activity or dup_tg.first_activity < main_tg.first_activity):
        main_tg.first_activity = dup_tg.first_activity
        fields_merged += 1
        print(f"  - Обновлена первая активность: {dup_tg.first_activity}")
    
    if dup_tg.custom_data:
        if not main_tg.custom_data:
            main_tg.custom_data = {}
        for key, value in dup_tg.custom_data.items():
            if key not in main_tg.custom_data:
                main_tg.custom_data[key] = value
                fields_merged += 1
                print(f"  - Перенесена custom_data: {key}")
    
    return fields_merged


def merge_django_user_data(main_user, dup_user):
    """Объединяет данные пользователей Django"""
    fields_merged = 0
    
    fields_to_merge = [
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('email', 'email'),
        ('phone', 'phone'),
        ('gender', 'gender'),
        ('country', 'country'),
        ('city', 'city'),
        ('vk_url', 'vk_url'),
        ('instagram_url', 'instagram_url'),
        ('timezone', 'timezone'),
        ('privacy_policy_version', 'privacy_policy_version'),
    ]
    
    for main_field, dup_field in fields_to_merge:
        main_value = getattr(main_user, main_field, None)
        dup_value = getattr(dup_user, dup_field, None)
        
        if (main_value is None or main_value == '') and dup_value:
            setattr(main_user, main_field, dup_value)
            fields_merged += 1
            print(f"  - Перенесено user.{main_field}: '{dup_value}'")
    
    if main_user.auth_ips and dup_user.auth_ips:
        existing_ips = {item.get('ip') for item in main_user.auth_ips if item.get('ip')}
        for ip_entry in dup_user.auth_ips:
            if ip_entry.get('ip') not in existing_ips:
                main_user.auth_ips.append(ip_entry)
                existing_ips.add(ip_entry.get('ip'))
                fields_merged += 1
        if len(main_user.auth_ips) > 10:
            main_user.auth_ips = main_user.auth_ips[-10:]
    elif dup_user.auth_ips and not main_user.auth_ips:
        main_user.auth_ips = dup_user.auth_ips
        fields_merged += 1
    
    if dup_user.meta_data:
        if not main_user.meta_data:
            main_user.meta_data = {}
        for key, value in dup_user.meta_data.items():
            if key not in main_user.meta_data:
                main_user.meta_data[key] = value
                fields_merged += 1
    
    return fields_merged


def find_duplicate_users(user):
    """
    Находит дублирующихся пользователей по:
    1. Email
    2. Телефону
    3. TelegramUser
    """
    duplicates = []
    
    # 1. Поиск по email
    if user.email:
        email_dups = User.objects.filter(
            email=user.email
        ).exclude(id=user.id)
        if email_dups.exists():
            duplicates.extend(list(email_dups))
            print(f"  Найдены дубли по email: {email_dups.count()}")
    
    # 2. Поиск по телефону
    if user.phone:
        phone_dups = User.objects.filter(
            phone=user.phone
        ).exclude(id=user.id)
        if phone_dups.exists():
            duplicates.extend(list(phone_dups))
            print(f"  Найдены дубли по телефону: {phone_dups.count()}")
    
    # 3. Поиск по TelegramUser
    if user.telegram_user:
        tg_dups = User.objects.filter(
            telegram_user=user.telegram_user
        ).exclude(id=user.id)
        if tg_dups.exists():
            duplicates.extend(list(tg_dups))
            print(f"  Найдены дубли по TelegramUser: {tg_dups.count()}")
    
    # 4. Поиск по username (если он похож на email)
    if user.username and '@' in user.username:
        username_dups = User.objects.filter(
            username=user.username
        ).exclude(id=user.id)
        if username_dups.exists():
            duplicates.extend(list(username_dups))
            print(f"  Найдены дубли по username: {username_dups.count()}")
    
    # Убираем дубликаты из списка
    unique_duplicates = list(set(duplicates))
    
    return unique_duplicates

def merge_users(main_user, dup_user):
    """
    Объединяет двух пользователей: все данные переносятся в main_user,
    dup_user удаляется
    """
    global _merging_in_progress
    
    _merging_in_progress = True
    
    try:
        print(f"  Объединяем пользователя {dup_user.username} -> {main_user.username}")
        
        # 1. Объединяем данные
        merge_django_user_data(main_user, dup_user)
        
        # 2. Переносим TelegramUser
        if dup_user.telegram_user and not main_user.telegram_user:
            main_user.telegram_user = dup_user.telegram_user
            main_user.telegram_verified = dup_user.telegram_verified
            print(f"  - Перенесен TelegramUser: {dup_user.telegram_user.telegram_id}")
        
        dup_user_id = dup_user.id
        
        # 3. Обновляем все внешние ключи
        # Таблица: telegram_users (user_id)
        TelegramUser.objects.filter(user_id=dup_user_id).update(user=main_user)
        
        # Таблица: blacklist (user_id, created_by_id)
        Blacklist.objects.filter(user_id=dup_user_id).update(user=main_user)
        Blacklist.objects.filter(created_by_id=dup_user_id).update(created_by=main_user)
        
        # Таблица: user_warnings (user_id, created_by_id)
        try:
            from users.models import UserWarning
            UserWarning.objects.filter(user_id=dup_user_id).update(user=main_user)
            UserWarning.objects.filter(created_by_id=dup_user_id).update(created_by=main_user)
        except ImportError:
            pass
        
        # Таблица: user_ip_history (user_id)
        try:
            from users.models import UserIPHistory
            UserIPHistory.objects.filter(user_id=dup_user_id).update(user=main_user)
        except ImportError:
            pass
        
        # Таблица: users_groups (user_id) - ManyToMany
        # Очищаем группы у дубля и добавляем к основному
        groups = list(dup_user.groups.all())
        if groups:
            main_user.groups.add(*groups)
            dup_user.groups.clear()
            print(f"  - Перенесены группы: {[g.name for g in groups]}")
        
        # Таблица: users_user_permissions (user_id) - ManyToMany
        permissions = list(dup_user.user_permissions.all())
        if permissions:
            main_user.user_permissions.add(*permissions)
            dup_user.user_permissions.clear()
            print(f"  - Перенесены права: {len(permissions)}")
        
        # Таблица: filer_folder (owner_id)
        try:
            from filer.models import Folder
            Folder.objects.filter(owner_id=dup_user_id).update(owner=main_user)
        except ImportError:
            pass
        
        # Таблица: filer_file (owner_id)
        try:
            from filer.models import File
            File.objects.filter(owner_id=dup_user_id).update(owner=main_user)
        except ImportError:
            pass
        
        # Таблица: filer_clipboard (user_id)
        try:
            from filer.models import Clipboard
            Clipboard.objects.filter(user_id=dup_user_id).update(user=main_user)
        except ImportError:
            pass
        
        # Таблица: filer_folderpermission (user_id)
        try:
            from filer.models import FolderPermission
            FolderPermission.objects.filter(user_id=dup_user_id).update(user=main_user)
        except ImportError:
            pass
        
        # Таблица: django_admin_log (user_id)
        from django.contrib.admin.models import LogEntry
        LogEntry.objects.filter(user_id=dup_user_id).update(user=main_user)
        
        # 4. Сохраняем основного пользователя
        main_user.save(update_fields=[
            'first_name', 'last_name', 'email', 'phone', 'gender',
            'country', 'city', 'vk_url', 'instagram_url', 'timezone',
            'privacy_policy_version', 'auth_ips', 'meta_data',
            'telegram_user', 'telegram_verified'
        ])
        
        # 5. Очищаем все внешние ключи у дубля (на случай, если что-то пропустили)
        TelegramUser.objects.filter(user_id=dup_user_id).update(user=None)
        Blacklist.objects.filter(user_id=dup_user_id).update(user=None)
        Blacklist.objects.filter(created_by_id=dup_user_id).update(created_by=None)
        
        try:
            from users.models import UserWarning
            UserWarning.objects.filter(user_id=dup_user_id).update(user=None)
            UserWarning.objects.filter(created_by_id=dup_user_id).update(created_by=None)
        except ImportError:
            pass
        
        try:
            from users.models import UserIPHistory
            UserIPHistory.objects.filter(user_id=dup_user_id).update(user=None)
        except ImportError:
            pass
        
        # Очищаем ManyToMany связи
        dup_user.groups.clear()
        dup_user.user_permissions.clear()
        
        # 6. Деактивируем дубль
        dup_user.is_active = False
        dup_user.save(update_fields=['is_active'])
        
        # 7. Принудительно удаляем дубль
        User.objects.filter(id=dup_user_id).delete()
        
        print(f"  - Пользователь {dup_user.username} удален")
        
    except Exception as e:
        print(f"  - Ошибка при объединении: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        _merging_in_progress = False
        
@receiver(pre_save, sender=User)
def check_and_merge_all_duplicates_before_save(sender, instance, **kwargs):
    """
    Перед сохранением пользователя проверяем дубли по всем полям
    """
    global _merging_in_progress
    
    # Если уже идет объединение, пропускаем
    if _merging_in_progress:
        print(f"[Сигнал pre_save] Пропускаем (идет объединение): {instance.username}")
        return
    
    print(f"\n[Сигнал pre_save] Проверка дублей для пользователя {instance.username or 'новый'}")
    
    # Если пользователь новый, пропускаем
    if not instance.pk:
        print("  Новый пользователь, пропускаем")
        return
    
    # Находим все дубли
    duplicates = find_duplicate_users(instance)
    
    if not duplicates:
        print("  Дублей не найдено")
        return
    
    print(f"  Всего найдено дублей: {len(duplicates)}")
    
    with transaction.atomic():
        main_user = instance
        
        # Объединяем все дубли
        for dup in duplicates:
            merge_users(main_user, dup)


@receiver(post_save, sender=User)
def merge_duplicate_telegram_connections(sender, instance, created, **kwargs):
    """
    После сохранения пользователя проверяем дубли в TelegramUser
    """
    global _merging_in_progress
    
    # Если уже идет объединение, пропускаем
    if _merging_in_progress:
        print(f"[Сигнал post_save] Пропускаем (идет объединение): {instance.username}")
        return
    
    print(f"\n[Сигнал post_save] Проверка TelegramUser для {instance.username}")
    
    # 1. Проверяем дубли по telegram_id
    if instance.telegram_user:
        same_telegram = TelegramUser.objects.filter(
            telegram_id=instance.telegram_user.telegram_id
        ).exclude(id=instance.telegram_user.id)
        
        if same_telegram.exists():
            print(f"  Найдены дубли по telegram_id: {same_telegram.count()}")
            with transaction.atomic():
                main_tg = instance.telegram_user
                
                for dup in same_telegram:
                    print(f"  Объединяем TelegramUser {dup.id} -> {main_tg.id}")
                    
                    # Объединяем данные
                    merge_telegram_user_data(main_tg, dup)
                    
                    # Если дубль связан с пользователем
                    if dup.user and dup.user != instance:
                        print(f"  Дубль связан с пользователем {dup.user.username}")
                        # Проверяем, не нужно ли объединить пользователей
                        _merging_in_progress = True
                        try:
                            merge_users(instance, dup.user)
                        finally:
                            _merging_in_progress = False
                    
                    # Переносим сообщения
                    TelegramMessage.objects.filter(user=dup).update(user=main_tg)
                    
                    # Переносим сессию
                    try:
                        dup_session = TelegramSession.objects.get(user=dup)
                        dup_session.user = main_tg
                        dup_session.save()
                    except TelegramSession.DoesNotExist:
                        pass
                    
                    # Обновляем ссылки у пользователей
                    User.objects.filter(telegram_user=dup).update(telegram_user=main_tg)
                    
                    # Удаляем дубль
                    dup.user = None
                    dup.save()
                    dup.delete()
                    print(f"  TelegramUser {dup.id} удален")
                
                main_tg.save()
    
    # 2. Проверяем TelegramUser без связи, но с таким же username как email
    if instance.email:
        orphan_tg = TelegramUser.objects.filter(
            username=instance.email,
            user__isnull=True
        )
        
        if orphan_tg.exists():
            print(f"  Найдены TelegramUser без связи с email {instance.email}: {orphan_tg.count()}")
            with transaction.atomic():
                for tg in orphan_tg:
                    if not instance.telegram_user:
                        print(f"  Связываем TelegramUser {tg.id} с пользователем {instance.username}")
                        tg.user = instance
                        tg.save()
                        
                        instance.telegram_user = tg
                        instance.telegram_verified = True
                        instance.save(update_fields=['telegram_user', 'telegram_verified'])
                    else:
                        print(f"  Объединяем TelegramUser {tg.id} с {instance.telegram_user.id}")
                        main_tg = instance.telegram_user
                        merge_telegram_user_data(main_tg, tg)
                        
                        TelegramMessage.objects.filter(user=tg).update(user=main_tg)
                        
                        try:
                            dup_session = TelegramSession.objects.get(user=tg)
                            dup_session.user = main_tg
                            dup_session.save()
                        except TelegramSession.DoesNotExist:
                            pass
                        
                        tg.user = None
                        tg.save()
                        tg.delete()
                        main_tg.save()


@receiver(pre_save, sender=TelegramUser)
def check_telegram_user_duplicates_before_save(sender, instance, **kwargs):
    """
    Перед сохранением TelegramUser проверяем дубли
    """
    global _merging_in_progress
    
    if _merging_in_progress:
        return
    
    if not instance.telegram_id:
        return
    
    print(f"\n[Сигнал TelegramUser pre_save] Проверка дублей для {instance.telegram_id}")
    
    duplicates = TelegramUser.objects.filter(
        telegram_id=instance.telegram_id
    ).exclude(id=instance.pk if instance.pk else None)
    
    if duplicates.exists():
        print(f"  Найдены дубли: {duplicates.count()}")
        
        with transaction.atomic():
            main_tg = instance
            for dup in duplicates:
                if not main_tg.user and dup.user:
                    main_tg, dup = dup, main_tg
                    print(f"  Основным стал TelegramUser с пользователем {main_tg.user.username}")
                
                print(f"  Объединяем дубль {dup.id} -> {main_tg.id}")
                merge_telegram_user_data(main_tg, dup)
                
                if dup.user and dup.user != main_tg.user:
                    if dup.user:
                        print(f"  Дубль связан с пользователем {dup.user.username}")
                        _merging_in_progress = True
                        try:
                            # Проверяем, не дублируются ли пользователи
                            user_duplicates = find_duplicate_users(dup.user)
                            if instance.user and instance.user in user_duplicates:
                                merge_users(instance.user, dup.user)
                            else:
                                dup.user.telegram_user = None
                                dup.user.telegram_verified = False
                                dup.user.save(update_fields=['telegram_user', 'telegram_verified'])
                        finally:
                            _merging_in_progress = False
                
                TelegramMessage.objects.filter(user=dup).update(user=main_tg)
                
                try:
                    dup_session = TelegramSession.objects.get(user=dup)
                    dup_session.user = main_tg
                    dup_session.save()
                except TelegramSession.DoesNotExist:
                    pass
                
                User.objects.filter(telegram_user=dup).update(telegram_user=main_tg)
                
                dup.user = None
                dup.save()
                dup.delete()
                print(f"  Дубль {dup.id} удален")
            
            main_tg.save()
            
            if instance.pk and instance.pk != main_tg.pk:
                for field in ['username', 'first_name', 'last_name', 'phone_number', 
                            'language_code', 'total_messages', 'last_activity', 
                            'first_activity', 'custom_data']:
                    setattr(instance, field, getattr(main_tg, field))
                instance.id = main_tg.id
                instance.pk = main_tg.pk


@receiver(post_save, sender=TelegramUser)
def check_telegram_user_after_save(sender, instance, created, **kwargs):
    """
    После сохранения TelegramUser проверяем дублирующиеся связи с пользователями
    """
    global _merging_in_progress
    
    if _merging_in_progress:
        return
    
    if not instance.user:
        return
    
    # Проверяем, существует ли еще пользователь
    try:
        User.objects.get(id=instance.user.id)
    except User.DoesNotExist:
        # Пользователь уже удален, очищаем связь
        instance.user = None
        instance.save(update_fields=['user'])
        return
    
    print(f"\n[Сигнал TelegramUser post_save] Проверка связей для {instance.telegram_id}")
    
    # Находим других пользователей с этим TelegramUser
    other_users = User.objects.filter(
        telegram_user=instance
    ).exclude(id=instance.user.id)
    
    if other_users.exists():
        print(f"  Найдены другие пользователи с этим TelegramUser: {other_users.count()}")
        
        with transaction.atomic():
            main_user = instance.user
            
            for user in other_users:
                # Проверяем, существует ли пользователь
                try:
                    User.objects.get(id=user.id)
                except User.DoesNotExist:
                    continue
                
                # Проверяем, не являются ли они дублями по email или телефону
                is_duplicate = False
                if user.email and main_user.email:
                    is_duplicate = user.email == main_user.email
                if not is_duplicate and user.phone and main_user.phone:
                    is_duplicate = user.phone == main_user.phone
                
                if is_duplicate:
                    print(f"  Объединяем пользователя {user.username} -> {main_user.username}")
                    _merging_in_progress = True
                    try:
                        merge_users(main_user, user)
                    finally:
                        _merging_in_progress = False
                else:
                    print(f"  Отвязываем пользователя {user.username} от Telegram")
                    # Просто отвязываем, не удаляем
                    user.telegram_user = None
                    user.telegram_verified = False
                    user.save(update_fields=['telegram_user', 'telegram_verified'])
                    
@receiver(user_logged_in)
def log_user_ip(sender, request, user, **kwargs):
    """
    Сигнал для записи IP адреса при входе пользователя
    """
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        location = None
        # Можно добавить определение местоположения:
        # try:
        #     import requests
        #     response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        #     if response.status_code == 200:
        #         data = response.json()
        #         location = f"{data.get('country', '')}, {data.get('city', '')}"
        # except:
        #     pass
        
        UserIPHistory.objects.create(
            user=user,
            ip_address=ip,
            location=location,
            user_agent=user_agent,
            is_successful=True
        )
        
        user.add_auth_ip(ip, user_agent)
    except Exception as e:
        print(f"Ошибка при записи IP: {e}")