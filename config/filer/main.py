from config import DEBUG

THUMBNAIL_HIGH_RESOLUTION = True  # для поддержки Retina дисплеев [citation:5]
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    # 'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',  # умное кадрирование [citation:1]
    'easy_thumbnails.processors.filters',
)

FILER_CANONICAL_URL = 'sharing/'  # для постоянных ссылок на файлы [citation:1]
FILER_DEBUG = DEBUG  # отключаем отладку в продакшене
FILER_ENABLE_LOGGING = True  # включаем логирование ошибок

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True  # Разрешить пользователям создавать папки
FILER_ENABLE_PERMISSIONS = True  # Включить права доступа к файлам

FILER_SUBJECT_LOCATION_IMAGE_DEBUG = DEBUG