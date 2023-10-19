import datetime as dt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-3j+(281vuc(f*)tyx#y9kjcellmi62%pez76cw@#&&22&*+%=='

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'schedules',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'schedulum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'schedulum.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CURRENT_MONTH = dt.date.today().month

CURRENT_YEAR = dt.date.today().year

NEXT_YEAR = dt.date.today().year + 1

VALIDATE_DATES = {
    'CURRENT_AUGUST': dt.date(year=CURRENT_YEAR, month=8, day=29),
    'CURRENT_END_AUGUST': dt.date(year=CURRENT_YEAR, month=8, day=31),
    'NEXT_AUGUST': dt.date(year=NEXT_YEAR, month=8, day=29),
    'NEXT_END_AUGUST': dt.date(year=NEXT_YEAR, month=8, day=31),
    'CURRENT_JULY': dt.date(year=CURRENT_YEAR, month=7, day=1),
    'CURRENT_START_JULY': dt.date(year=CURRENT_YEAR, month=7, day=6),
    'NEXT_JULY': dt.date(year=NEXT_YEAR, month=7, day=1),
    'NEXT_START_JULY': dt.date(year=NEXT_YEAR, month=7, day=6)
}

RUSSIAN_MONTHS = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}
