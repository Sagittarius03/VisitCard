from django import forms
from django.utils.safestring import mark_safe


class PhoneMaskInput(forms.TextInput):
    """
    Виджет для ввода телефона с маской +7 (XXX) XXX-XX-XX
    """
    class Media:
        js = ('admin/js/phone_mask.js',)
        css = {
            'all': ('admin/css/phone_mask.css',)  # Опционально
        }

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'phone-mask-input',
            'placeholder': '+7 (XXX) XXX-XX-XX',
            'autocomplete': 'off',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Если значение есть, форматируем его
        if value:
            formatted = self.format_phone(value)
        else:
            formatted = '+7'
        
        # Добавляем data-атрибут с raw значением
        if attrs is None:
            attrs = {}
        attrs['data-raw-value'] = value or '+7'
        
        # Рендерим поле
        html = super().render(name, formatted, attrs, renderer)
        
        # Добавляем скрипт инициализации
        script = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Инициализация поля
                const input = document.querySelector('[name="%s"]');
                if (input && !input.value) {
                    input.value = '+7';
                }
                // Триггерим событие для инициализации маски
                if (input) {
                    input.dispatchEvent(new Event('input'));
                }
            });
        </script>
        """ % name
        
        return mark_safe(html + script)

    def format_phone(self, value):
        """
        Форматирует номер телефона в красивый вид
        """
        # Убираем все нецифровые символы
        digits = ''.join(filter(str.isdigit, str(value)))
        
        # Если номер начинается с 8, заменяем на 7
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        
        # Если номер не начинается с 7, добавляем
        if not digits.startswith('7'):
            digits = '7' + digits
        
        # Ограничиваем длину
        digits = digits[:11]
        
        # Форматируем
        if len(digits) <= 1:
            return '+' + digits
        elif len(digits) <= 4:
            return '+' + digits[0] + ' (' + digits[1:]
        elif len(digits) <= 7:
            return '+' + digits[0] + ' (' + digits[1:4] + ') ' + digits[4:]
        elif len(digits) <= 9:
            return '+' + digits[0] + ' (' + digits[1:4] + ') ' + digits[4:7] + '-' + digits[7:]
        else:
            return '+' + digits[0] + ' (' + digits[1:4] + ') ' + digits[4:7] + '-' + digits[7:9] + '-' + digits[9:11]