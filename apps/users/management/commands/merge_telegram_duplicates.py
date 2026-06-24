from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from telega.models import TelegramUser, TelegramMessage, TelegramSession
from users.models import Blacklist
from users.signals import merge_telegram_user_data, merge_django_user_data

User = get_user_model()


class Command(BaseCommand):
    help = 'Объединяет дублирующиеся связи TelegramUser и пользователей с интерактивным выбором'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Автоматически объединять без подтверждения (выбирает объект с наибольшим количеством заполненных полей)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, что будет сделано, без фактических изменений',
        )

    def handle(self, *args, **options):
        auto_mode = options.get('auto', False)
        dry_run = options.get('dry_run', False)
        
        self.stdout.write('🔍 Поиск дублей...')
        
        all_duplicates = self.find_duplicates()
        
        if not all_duplicates:
            self.stdout.write(self.style.SUCCESS('\n✅ Дублей не найдено!'))
            return
        
        if dry_run:
            self.show_duplicates_preview(all_duplicates)
            self.stdout.write(
                self.style.WARNING(
                    f'\n🔍 Найдено {len(all_duplicates)} дублей. '
                    'Используйте без --dry-run для объединения.'
                )
            )
            return
        
        # Обрабатываем каждый дубль
        merged_count = 0
        with transaction.atomic():
            for idx, item in enumerate(all_duplicates, 1):
                self.stdout.write(f'\n{"="*60}')
                self.stdout.write(f'Дубль #{idx} из {len(all_duplicates)}')
                self.stdout.write(f'{"="*60}')
                
                if auto_mode:
                    # Автоматический режим - выбираем объект с большим количеством заполненных полей
                    should_merge = True
                    main_obj, dup_obj, obj_type = self.auto_select_main(item)
                else:
                    # Интерактивный режим
                    main_obj, dup_obj, obj_type = self.interactive_select_main(item)
                    if not main_obj:
                        self.stdout.write(self.style.WARNING('  ⏭️ Пропускаем этот дубль'))
                        continue
                    
                    should_merge = self.confirm_merge(main_obj, dup_obj, obj_type)
                
                if not should_merge:
                    self.stdout.write(self.style.WARNING('  ⏭️ Пропускаем этот дубль'))
                    continue
                
                # Выполняем объединение
                try:
                    self.merge_objects(main_obj, dup_obj, obj_type)
                    merged_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ {obj_type} успешно объединен!'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Обработано {merged_count} дублей из {len(all_duplicates)}')
        )

    def find_duplicates(self):
        """Находит все дубли"""
        from django.db.models import Count
        all_duplicates = []
        
        # 1. Дубли по telegram_id
        duplicate_telegram_ids = TelegramUser.objects.values('telegram_id').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for item in duplicate_telegram_ids:
            tg_id = item['telegram_id']
            tgs = TelegramUser.objects.filter(telegram_id=tg_id)
            
            main_tg = tgs.filter(user__isnull=False).first()
            if not main_tg:
                main_tg = tgs.first()
            
            duplicates = tgs.exclude(id=main_tg.id)
            for dup in duplicates:
                all_duplicates.append({
                    'type': 'telegram_duplicate',
                    'main': main_tg,
                    'duplicate': dup,
                    'main_user': main_tg.user if main_tg.user else None,
                    'dup_user': dup.user if dup.user else None,
                })
        
        # 2. Дубли по user (несколько TelegramUser у одного пользователя)
        users_with_duplicates = User.objects.annotate(
            tg_count=Count('telegram_users')
        ).filter(tg_count__gt=1)
        
        for user in users_with_duplicates:
            tgs = TelegramUser.objects.filter(user=user)
            
            main_tg = user.telegram_user
            if not main_tg:
                main_tg = tgs.first()
            
            duplicates = tgs.exclude(id=main_tg.id)
            for dup in duplicates:
                all_duplicates.append({
                    'type': 'user_duplicate',
                    'main': main_tg,
                    'duplicate': dup,
                    'main_user': user,
                    'dup_user': user,
                })
        
        # 3. Дубли в пользователях Django (несколько пользователей на один TelegramUser)
        duplicate_users = User.objects.values('telegram_user_id').annotate(
            count=Count('id')
        ).filter(count__gt=1, telegram_user_id__isnull=False)
        
        for item in duplicate_users:
            tg_user_id = item['telegram_user_id']
            users = User.objects.filter(telegram_user_id=tg_user_id)
            
            try:
                tg_user = TelegramUser.objects.get(id=tg_user_id)
            except TelegramUser.DoesNotExist:
                continue
            
            # Находим основного пользователя по заполненным полям
            main_user = self.find_best_user(users)
            
            for user in users.exclude(id=main_user.id):
                all_duplicates.append({
                    'type': 'django_user_duplicate',
                    'main': tg_user,
                    'duplicate': None,
                    'main_user': main_user,
                    'dup_user': user,
                })
        
        return all_duplicates

    def find_best_user(self, users):
        """Находит пользователя с наибольшим количеством заполненных полей"""
        best_user = None
        max_fields = -1
        
        for user in users:
            filled_fields = 0
            if user.first_name: filled_fields += 1
            if user.last_name: filled_fields += 1
            if user.email: filled_fields += 1
            if user.phone: filled_fields += 1
            if user.vk_url: filled_fields += 1
            if user.instagram_url: filled_fields += 1
            if user.country: filled_fields += 1
            if user.city: filled_fields += 1
            # if user.bio: filled_fields += 1
            
            if filled_fields > max_fields:
                max_fields = filled_fields
                best_user = user
        
        return best_user or users.first()

    def show_user_info(self, user, label):
        """Показывает информацию о пользователе"""
        if not user:
            return "Отсутствует"
        
        fields = []
        if user.username: fields.append(f"username={user.username}")
        if user.first_name: fields.append(f"first_name={user.first_name}")
        if user.last_name: fields.append(f"last_name={user.last_name}")
        if user.email: fields.append(f"email={user.email}")
        if user.phone: fields.append(f"phone={user.phone}")
        if user.vk_url: fields.append(f"vk={user.vk_url}")
        if user.instagram_url: fields.append(f"instagram={user.instagram_url}")
        if user.country: fields.append(f"country={user.country}")
        if user.city: fields.append(f"city={user.city}")
        if user.telegram_user: fields.append(f"telegram_id={user.telegram_user.telegram_id}")
        
        return f"{label}: {', '.join(fields) if fields else 'нет данных'}"

    def show_telegram_info(self, tg, label):
        """Показывает информацию о TelegramUser"""
        if not tg:
            return "Отсутствует"
        
        fields = []
        if tg.telegram_id: fields.append(f"telegram_id={tg.telegram_id}")
        if tg.username: fields.append(f"tg_username=@{tg.username}")
        if tg.first_name: fields.append(f"first_name={tg.first_name}")
        if tg.last_name: fields.append(f"last_name={tg.last_name}")
        if tg.phone_number: fields.append(f"phone={tg.phone_number}")
        fields.append(f"messages={tg.total_messages}")
        if tg.user: fields.append(f"django_user={tg.user.username}")
        
        return f"{label}: {', '.join(fields)}"

    def show_duplicates_preview(self, duplicates):
        """Показывает превью найденных дублей"""
        self.stdout.write('\n📋 Найденные дубли:\n')
        for idx, item in enumerate(duplicates, 1):
            self.stdout.write(f'{idx}. Тип: {item["type"]}')
            
            if item['type'] == 'django_user_duplicate':
                self.stdout.write(f'   Основной пользователь: {self.show_user_info(item["main_user"], "")}')
                self.stdout.write(f'   Дублирующий пользователь: {self.show_user_info(item["dup_user"], "")}')
            else:
                self.stdout.write(f'   Основной TelegramUser: {self.show_telegram_info(item["main"], "")}')
                self.stdout.write(f'   Дублирующий TelegramUser: {self.show_telegram_info(item["duplicate"], "")}')
                if item['main_user']:
                    self.stdout.write(f'   Пользователь основного: {self.show_user_info(item["main_user"], "")}')
                if item['dup_user']:
                    self.stdout.write(f'   Пользователь дубля: {self.show_user_info(item["dup_user"], "")}')
            self.stdout.write('')

    def interactive_select_main(self, item):
        """Интерактивный выбор основного объекта"""
        self.stdout.write('\n📋 Информация о дубле:')
        self.stdout.write('-' * 40)
        
        obj_type = item['type']
        
        if obj_type == 'django_user_duplicate':
            # Выбор между пользователями Django
            user1 = item['main_user']
            user2 = item['dup_user']
            
            self.stdout.write('\n1️⃣ Основной пользователь (по умолчанию):')
            self.stdout.write(f'   {self.show_user_info(user1, "")}')
            self.stdout.write(f'   TelegramUser: {self.show_telegram_info(user1.telegram_user, "")}')
            
            self.stdout.write('\n2️⃣ Дублирующий пользователь:')
            self.stdout.write(f'   {self.show_user_info(user2, "")}')
            self.stdout.write(f'   TelegramUser: {self.show_telegram_info(user2.telegram_user, "")}')
            
            choice = input('\nВыберите основной объект (1/2, Enter - 1): ').strip()
            
            if choice == '2':
                return user2, user1, obj_type
            return user1, user2, obj_type
        
        else:
            # Выбор между TelegramUser
            main_tg = item['main']
            dup_tg = item['duplicate']
            
            self.stdout.write('\n1️⃣ Основной TelegramUser:')
            self.stdout.write(f'   {self.show_telegram_info(main_tg, "")}')
            if item['main_user']:
                self.stdout.write(f'   Связан с пользователем: {self.show_user_info(item["main_user"], "")}')
            
            self.stdout.write('\n2️⃣ Дублирующий TelegramUser:')
            self.stdout.write(f'   {self.show_telegram_info(dup_tg, "")}')
            if item['dup_user']:
                self.stdout.write(f'   Связан с пользователем: {self.show_user_info(item["dup_user"], "")}')
            
            choice = input('\nВыберите основной объект (1/2, Enter - 1): ').strip()
            
            if choice == '2':
                return dup_tg, main_tg, obj_type
            return main_tg, dup_tg, obj_type

    def auto_select_main(self, item):
        """Автоматический выбор основного объекта"""
        obj_type = item['type']
        
        if obj_type == 'django_user_duplicate':
            user1 = item['main_user']
            user2 = item['dup_user']
            
            # Считаем заполненные поля
            count1 = self.count_user_fields(user1)
            count2 = self.count_user_fields(user2)
            
            if count2 > count1:
                self.stdout.write(f'  Автоматически выбран пользователь {user2.username} ({count2} полей)')
                return user2, user1, obj_type
            self.stdout.write(f'  Автоматически выбран пользователь {user1.username} ({count1} полей)')
            return user1, user2, obj_type
        
        else:
            main_tg = item['main']
            dup_tg = item['duplicate']
            
            # Считаем заполненные поля
            count1 = self.count_telegram_fields(main_tg)
            count2 = self.count_telegram_fields(dup_tg)
            
            # Также учитываем наличие связанного пользователя
            if item['main_user'] and not item['dup_user']:
                return main_tg, dup_tg, obj_type
            elif item['dup_user'] and not item['main_user']:
                return dup_tg, main_tg, obj_type
            
            if count2 > count1:
                self.stdout.write(f'  Автоматически выбран TelegramUser {dup_tg.telegram_id} ({count2} полей)')
                return dup_tg, main_tg, obj_type
            self.stdout.write(f'  Автоматически выбран TelegramUser {main_tg.telegram_id} ({count1} полей)')
            return main_tg, dup_tg, obj_type

    def count_user_fields(self, user):
        """Считает количество заполненных полей у пользователя"""
        count = 0
        if user.first_name: count += 1
        if user.last_name: count += 1
        if user.email: count += 1
        if user.phone: count += 1
        if user.vk_url: count += 1
        if user.instagram_url: count += 1
        if user.country: count += 1
        if user.city: count += 1
        return count

    def count_telegram_fields(self, tg):
        """Считает количество заполненных полей у TelegramUser"""
        count = 0
        if tg.username: count += 1
        if tg.first_name: count += 1
        if tg.last_name: count += 1
        if tg.phone_number: count += 1
        if tg.language_code: count += 1
        if tg.user: count += 1
        count += tg.total_messages // 10  # Каждые 10 сообщений считаем за поле
        return count

    def confirm_merge(self, main_obj, dup_obj, obj_type):
        """Подтверждение объединения"""
        self.stdout.write('\n⚠️  Будет выполнено объединение:')
        
        if obj_type == 'django_user_duplicate':
            self.stdout.write(f'  Основной: {self.show_user_info(main_obj, "")}')
            self.stdout.write(f'  Удаляемый: {self.show_user_info(dup_obj, "")}')
            self.stdout.write(f'  TelegramUser будет перенесен на основного пользователя')
        else:
            self.stdout.write(f'  Основной: {self.show_telegram_info(main_obj, "")}')
            self.stdout.write(f'  Удаляемый: {self.show_telegram_info(dup_obj, "")}')
            if dup_obj.user:
                self.stdout.write(f'  Пользователь дубля: {self.show_user_info(dup_obj.user, "")}')
        
        choice = input('\nПродолжить объединение? (y/N): ').strip().lower()
        return choice in ['y', 'yes', 'д', 'да']

    def merge_objects(self, main_obj, dup_obj, obj_type):
        """Выполняет объединение объектов"""
        if obj_type == 'django_user_duplicate':
            # Объединяем пользователей Django
            main_user = main_obj
            dup_user = dup_obj
            
            # Объединяем данные
            merge_django_user_data(main_user, dup_user)
            
            # Переносим TelegramUser
            if dup_user.telegram_user and not main_user.telegram_user:
                main_user.telegram_user = dup_user.telegram_user
                main_user.telegram_verified = True
                main_user.save(update_fields=['telegram_user', 'telegram_verified'])
            
            # Обновляем связи
            TelegramUser.objects.filter(user=dup_user).update(user=main_user)
            Blacklist.objects.filter(user=dup_user).update(user=main_user)
            Blacklist.objects.filter(created_by=dup_user).update(created_by=main_user)
            
            # Деактивируем и удаляем дубль
            dup_user.is_active = False
            dup_user.save()
            dup_user.delete()
            
        else:
            # Объединяем TelegramUser
            main_tg = main_obj
            dup_tg = dup_obj
            
            # Объединяем данные
            merge_telegram_user_data(main_tg, dup_tg)
            
            # Если дубль связан с пользователем
            if dup_tg.user and dup_tg.user != main_tg.user:
                # Обновляем ссылку в пользователе
                dup_tg.user.telegram_user = None
                dup_tg.user.telegram_verified = False
                dup_tg.user.save(update_fields=['telegram_user', 'telegram_verified'])
            
            # Переносим сообщения
            TelegramMessage.objects.filter(user=dup_tg).update(user=main_tg)
            
            # Переносим сессию
            try:
                dup_session = TelegramSession.objects.get(user=dup_tg)
                dup_session.user = main_tg
                dup_session.save()
            except TelegramSession.DoesNotExist:
                pass
            
            # Обновляем ссылки в пользователях
            User.objects.filter(telegram_user=dup_tg).update(telegram_user=main_tg)
            
            # Удаляем дубль
            dup_tg.user = None
            dup_tg.save()
            dup_tg.delete()
            
            main_tg.save()