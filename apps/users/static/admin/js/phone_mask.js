// static/admin/js/phone_mask.js
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('.phone-mask-input');
    
    phoneInputs.forEach(function(input) {
        // Инициализация
        if (!input.value || input.value === '') {
            input.value = '+7';
        }
        
        // Сохраняем сырое значение
        let rawValue = input.value.replace(/\D/g, '');
        if (!rawValue.startsWith('7') && rawValue.length > 0) {
            rawValue = '7' + rawValue;
        }
        if (rawValue.length === 0) rawValue = '7';
        input.dataset.rawValue = '+' + rawValue;
        
        // Форматируем при загрузке
        formatPhone(input);
        
        // Обработка ввода
        input.addEventListener('input', function(e) {
            // Получаем текущую позицию курсора
            const cursorPos = this.selectionStart;
            
            // Получаем сырое значение
            let raw = this.dataset.rawValue || '+7';
            raw = raw.replace(/\D/g, '');
            
            // Определяем, что было введено
            const oldLength = raw.length;
            
            // Получаем новое значение
            let newValue = this.value.replace(/\D/g, '');
            
            // Если пользователь удалил символы (backspace)
            if (newValue.length < oldLength) {
                // Удаляем последний символ из raw
                raw = raw.slice(0, -1);
                if (raw.length < 1) raw = '7';
            } else {
                // Добавляем цифры
                let digits = newValue.slice(oldLength);
                raw += digits;
                // Ограничиваем 11 цифрами (7 + 10)
                if (raw.length > 11) raw = raw.slice(0, 11);
            }
            
            // Обновляем сырое значение
            this.dataset.rawValue = '+' + raw;
            
            // Форматируем
            formatPhone(this);
            
            // Восстанавливаем позицию курсора
            const newPos = getCorrectCursorPosition(this, cursorPos);
            this.setSelectionRange(newPos, newPos);
        });
        
        // Обработка клавиш
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace') {
                e.preventDefault();
                let raw = this.dataset.rawValue || '+7';
                raw = raw.replace(/\D/g, '');
                if (raw.length > 1) {
                    raw = raw.slice(0, -1);
                }
                if (raw.length < 1) raw = '7';
                this.dataset.rawValue = '+' + raw;
                formatPhone(this);
                
                // Устанавливаем курсор в конец
                const pos = this.value.length;
                this.setSelectionRange(pos, pos);
            }
        });
        
        // Перед отправкой формы
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                const raw = input.dataset.rawValue || '+7';
                input.value = raw;
            });
        }
    });
});

function formatPhone(input) {
    let raw = input.dataset.rawValue || '+7';
    raw = raw.replace(/\D/g, '');
    
    if (raw.length === 0) raw = '7';
    if (raw.length > 11) raw = raw.slice(0, 11);
    
    // Форматируем для отображения
    let formatted = '+7';
    if (raw.length > 1) {
        formatted = '+' + raw[0];
        if (raw.length > 1) formatted += ' (' + raw.slice(1, 4);
        if (raw.length > 4) formatted += ') ' + raw.slice(4, 7);
        if (raw.length > 7) formatted += '-' + raw.slice(7, 9);
        if (raw.length > 9) formatted += '-' + raw.slice(9, 11);
    }
    
    input.value = formatted;
    input.dataset.rawValue = '+' + raw;
}

function getCorrectCursorPosition(input, oldPos) {
    const raw = input.dataset.rawValue || '+7';
    const formatted = input.value;
    
    // Находим позицию в отформатированной строке
    let pos = 0;
    let digitCount = 0;
    
    for (let i = 0; i < formatted.length; i++) {
        if (formatted[i] >= '0' && formatted[i] <= '9') {
            digitCount++;
            if (digitCount === raw.length - 1) {
                pos = i + 1;
                break;
            }
        }
    }
    
    return Math.min(pos, formatted.length);
}