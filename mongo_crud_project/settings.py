"""
Django settings for mongo_crud_project.
"""

import os
from pathlib import Path
<<<<<<< HEAD
import dj_database_url
import mongoengine
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables explicitly from .env in BASE_DIR
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep this secret in production!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-me-in-production')

# Set DEBUG to False in production via environment variable
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Trusted origins for CSRF POST requests when deployed
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",  # Hooks into MongoAuthMiddleware
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

INSTALLED_APPS = [
=======
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep this secret in production, this is fine for local dev
SECRET_KEY = 'django-insecure-dev-key-change-me-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # rest framework added for testing apis to postman
    'rest_framework',

>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',

    # Local apps
=======
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    'items',
]

AUTHENTICATION_BACKENDS = [
    'items.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
<<<<<<< HEAD
    'whitenoise.middleware.WhiteNoiseMiddleware',
=======
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
<<<<<<< HEAD
    'django.contrib.messages.middleware.MessageMiddleware',
=======
    'django.contrib.messages.middleware.MessageMiddleware',  # Placed above custom middlewares
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    'items.middleware.PendingApprovalMiddleware',
    'items.middleware.AgeRestrictionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mongo_crud_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
<<<<<<< HEAD
        'DIRS': [BASE_DIR / 'templates'],
=======
        'DIRS': [],
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
<<<<<<< HEAD
=======
                'items.context_processors.cart',
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
            ],
        },
    },
]

WSGI_APPLICATION = 'mongo_crud_project.wsgi.application'

<<<<<<< HEAD
# ---------------------------------------------------------------------------
# 1. Relational DB: Neon PostgreSQL (for Django Auth, Admin, and Sessions)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to local SQLite if DATABASE_URL is missing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }




# 3. Non-Relational DB: MongoEngine (for MongoDB Atlas App Data)
# ---------------------------------------------------------------------------
MONGO_URI = os.getenv('MONGO_URI')
if MONGO_URI:
    mongoengine.connect(host=MONGO_URI)
=======
# Django's own auth/admin/sessions still use SQLite (they expect a relational DB).
# The `items` app itself talks to MongoDB directly via MongoEngine (see bottom of file).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
<<<<<<< HEAD
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

=======

# Needed for the image upload feature (ImageField / FileField via Pillow)
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

<<<<<<< HEAD
=======
# ---------------------------------------------------------------------------
# MongoEngine connection (MongoDB Atlas)
# ---------------------------------------------------------------------------
import mongoengine

MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Check your .env file.")

mongoengine.connect(host=MONGO_URI)

>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'