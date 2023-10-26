import datetime
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = (os.getenv('DEBUG', 'False') == 'True')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
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

TEMPLATES_DIRS = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
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

CSRF_FAILURE_VIEW = 'schedules.views.csrf_failure'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'schedules:index'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static_backend/'

STATICFILES_DIRS = [
    BASE_DIR / 'static_backend',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CURRENT_MONTH = datetime.date.today().month

CURRENT_YEAR = datetime.date.today().year

NEXT_YEAR = datetime.date.today().year + 1

VALIDATE_DATES = {
    'CURRENT_AUGUST': datetime.date(year=CURRENT_YEAR, month=8, day=29),
    'CURRENT_END_AUGUST': datetime.date(year=CURRENT_YEAR, month=8, day=31),
    'NEXT_AUGUST': datetime.date(year=NEXT_YEAR, month=8, day=29),
    'NEXT_END_AUGUST': datetime.date(year=NEXT_YEAR, month=8, day=31),
    'CURRENT_JULY': datetime.date(year=CURRENT_YEAR, month=7, day=1),
    'CURRENT_START_JULY': datetime.date(year=CURRENT_YEAR, month=7, day=6),
    'NEXT_JULY': datetime.date(year=NEXT_YEAR, month=7, day=1),
    'NEXT_START_JULY': datetime.date(year=NEXT_YEAR, month=7, day=6)
}
