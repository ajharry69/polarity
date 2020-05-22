"""
Django settings for polarity project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

from django.conf import settings
from django.utils.encoding import force_str

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bi3m^im$z*0i!hk4x1s^*a-8vkf-ew7-!7%7b(nnb*mya=mfo$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polls.apps.PollsConfig',
    'api.apps.ApiConfig',
    'quickstart.apps.QuickstartConfig',
    'snippets.apps.SnippetsConfig',
    'xauth.apps.XauthConfig',
    'rest_framework',
    'django_extensions',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'polarity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'polarity.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'polarity.sqlite3'),
    }
}

# Use recommended argon2 for password hashing
# https://docs.djangoproject.com/en/3.0/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

XENTLY_AUTH = {
    # occasionally included in emails sent by the API to your users for familiarity
    'APP_NAME': 'Xently',
    'TOKEN_KEY': force_str(SECRET_KEY),
    'TOKEN_EXPIRY': timedelta(days=60),
    # string. Email addresses to which account / auth-related replies are to be sent.
    # Also permitted: "Name <email-address>"
    'REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES': [
        settings.EMAIL_HOST_USER
    ],
    # string. Email used to send verification code.
    # Also permitted: "Name <email-address>"
    'ACCOUNTS_EMAIL': settings.EMAIL_HOST_USER,
    'ACCOUNTS_EMAIL_PASSWORD': settings.EMAIL_HOST_PASSWORD,
    'VERIFICATION_CODE_LENGTH': 6,
    'TEMPORARY_PASSWORD_LENGTH': 8,
    'VERIFICATION_CODE_EXPIRY': timedelta(hours=1),
    'TEMPORARY_PASSWORD_EXPIRY': timedelta(minutes=30),
    # period within which a user is considered new since account creation date
    'NEWBIE_VALIDITY_PERIOD': timedelta(days=1),
    'AUTO_HASH_PASSWORD_ON_SAVE': False,
}

CELERY_BROKER_URL = 'pyamqp://guest@localhost//'

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_BACKEND = 'django-db'

CELERY_CACHE_BACKEND = 'django-cache'

AUTH_USER_MODEL = 'xauth.User'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
