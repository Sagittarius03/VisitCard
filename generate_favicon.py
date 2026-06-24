import os
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

def enhance_logo_for_favicon(input_path, output_path, size=None, add_border=False):
    """
    Улучшает PNG-логотип для favicon:
    - Повышает резкость и контраст
    - Оптимизирует цвета
    - Добавляет обводку для мелких размеров
    """
    try:
        # Открываем изображение
        img = Image.open(input_path)
        
        # Конвертируем в RGBA если нужно
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Для мелких размеров применяем улучшения
        if size and size <= 64:
            # 1. Увеличиваем контрастность
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            
            # 2. Повышаем насыщенность (для зеленых оттенков)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            
            # 3. Увеличиваем резкость
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # 4. Добавляем обводку для лучшей видимости
            if add_border:
                img = add_glow_border(img, size)
        
        # Изменяем размер с высоким качеством
        if size:
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Сохраняем с оптимизацией
        img.save(output_path, 'PNG', optimize=True)
        print(f'✅ {os.path.basename(output_path)} ({size}x{size})')
        return True
        
    except Exception as e:
        print(f'❌ Ошибка при обработке {input_path}: {e}')
        return False

def add_glow_border(img, size):
    """Добавляет зеленое свечение вокруг логотипа"""
    try:
        # Создаем маску из альфа-канала
        alpha = img.split()[3] if img.mode == 'RGBA' else None
        
        if alpha:
            # Размер обводки
            border = max(2, size // 16)
            
            # Создаем новое изображение с обводкой
            new_size = (img.width + border * 2, img.height + border * 2)
            new_img = Image.new('RGBA', new_size, (0, 0, 0, 0))
            
            # Создаем обводку с зеленым цветом
            border_mask = alpha.filter(ImageFilter.MaxFilter(border * 2 + 1))
            
            # Цвет обводки (зеленый с градиентом)
            glow_color = (0, 212, 170, 180)  # #00d4aa с прозрачностью
            
            # Создаем слой с обводкой
            border_layer = Image.new('RGBA', new_size, (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_layer)
            
            # Рисуем круглую обводку
            for i in range(border, 0, -1):
                alpha_val = int(180 * (i / border))
                color = (0, 212, 170, alpha_val)
                padding = border - i
                border_draw.ellipse(
                    [padding, padding, new_size[0] - padding, new_size[1] - padding],
                    outline=color,
                    width=1
                )
            
            # Вставляем оригинальное изображение
            new_img.paste(img, (border, border), img)
            
            # Комбинируем с обводкой
            result = Image.alpha_composite(border_layer, new_img)
            return result
        
        return img
    except Exception as e:
        print(f'⚠️ Ошибка добавления обводки: {e}')
        return img

def create_favicon_set(source_path, output_dir):
    """Создает полный набор иконок из PNG"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(source_path):
        print(f'❌ Файл не найден: {source_path}')
        return False
    
    print(f'📄 Исходный PNG: {source_path}')
    print('🔄 Улучшение и создание иконок...\n')
    
    # Размеры для разных иконок
    icon_sizes = {
        'favicon-16x16.png': 16,
        'favicon-32x32.png': 32,
        'favicon-64x64.png': 64,
        'apple-touch-icon.png': 180,
        'icon-192x192.png': 192,
        'icon-256x256.png': 256,
        'icon-512x512.png': 512,
        'social-preview.png': 128,
    }
    
    # Создаем иконки
    for filename, size in icon_sizes.items():
        output_path = os.path.join(output_dir, filename)
        # Для favicon добавляем обводку
        add_border = size <= 64
        enhance_logo_for_favicon(source_path, output_path, size, add_border)
    
    # Создаем favicon.ico
    try:
        ico_path = os.path.join(output_dir, 'favicon.ico')
        img16 = Image.open(os.path.join(output_dir, 'favicon-16x16.png'))
        img32 = Image.open(os.path.join(output_dir, 'favicon-32x32.png'))
        
        img32.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32)], append_images=[img16])
        print(f'✅ favicon.ico')
    except Exception as e:
        print(f'⚠️ Ошибка favicon.ico: {e}')
    
    # Создаем site.webmanifest
    manifest = {
        "name": "LeoForge",
        "short_name": "LeoForge",
        "description": "Личный лаунчер и портфолио разработчика",
        "icons": [
            {
                "src": "/static/icon/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/icon/icon-256x256.png",
                "sizes": "256x256",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/icon/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "theme_color": "#0a0f14",
        "background_color": "#0a0f14",
        "display": "standalone",
        "start_url": "/",
        "scope": "/"
    }
    
    with open(os.path.join(output_dir, 'site.webmanifest'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print('✅ site.webmanifest')
    
    # Создаем browserconfig.xml
    browserconfig = '''<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
    <msapplication>
        <tile>
            <square150x150logo src="/static/icon/icon-192x192.png"/>
            <TileColor>#0a0f14</TileColor>
        </tile>
    </msapplication>
</browserconfig>'''
    
    with open(os.path.join(output_dir, 'browserconfig.xml'), 'w', encoding='utf-8') as f:
        f.write(browserconfig)
    print('✅ browserconfig.xml')
    
    return True

if __name__ == '__main__':
    # Используем PNG вместо SVG
    source_path = 'static/icon/logo.png'
    output_dir = 'static/icon'
    
    print('=' * 50)
    print('🎨 УЛУЧШЕНИЕ ЛОГОТИПА ДЛЯ FAVICON')
    print('=' * 50)
    
    if os.path.exists(source_path):
        success = create_favicon_set(source_path, output_dir)
        
        if success:
            print('\n' + '=' * 50)
            print('✅ ВСЕ ИКОНКИ СОЗДАНЫ!')
            print('=' * 50)
            print('''
💚 УЛУЧШЕНИЯ ПРИМЕНЕНЫ:
   • Повышена резкость для мелких размеров
   • Увеличен контраст и насыщенность
   • Добавлена зеленая обводка для favicon
   • Оптимизированы цвета для лучшей видимости
   • Зеленые оттенки усилены

📁 ВСЕ ФАЙЛЫ СОЗДАНЫ:
   • favicon.ico — для всех браузеров
   • favicon-16x16.png, favicon-32x32.png, favicon-64x64.png
   • apple-touch-icon.png — для iOS
   • icon-192x192.png, icon-256x256.png, icon-512x512.png — для PWA
   • social-preview.png — для соцсетей
   • site.webmanifest — манифест
   • browserconfig.xml — для IE
            ''')
    else:
        print(f'❌ Файл не найден: {source_path}')
        print('\n💡 Сохраните ваш PNG-логотип по пути:')
        print(f'   {source_path}')