SYSTEM_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ADDITIONAL_MIDDLEWARE = [
    'config.middleware.xframe.ConditionalXFrameOptionsMiddleware',
    'config.middleware.jinja2.Jinja2GlobalRequestMiddleware',
]

MIDDLEWARE = SYSTEM_MIDDLEWARE + ADDITIONAL_MIDDLEWARE