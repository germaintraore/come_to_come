"""
2S informatique Plus - Come To Code
Configuration Django principale - Base de donnees PostgreSQL
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# CHARGEMENT DU FICHIER .env (sans dependance externe)
# ============================================================
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()


def get_env(key, default=None):
    return os.environ.get(key, default)


SECRET_KEY = get_env(
    'DJANGO_SECRET_KEY',
    'django-insecure-ctc-2s-informatique-plus-change-in-production-2025!'
)

DEBUG = str(get_env('DJANGO_DEBUG', 'True')).strip().lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']  # Permet l'acces depuis tout le reseau local

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'devoirs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


DATABASE_URL = get_env('DATABASE_URL') or os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # ============================================================
    # BASE DE DONNEES - PostgreSQL (Local)
    # ============================================================
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     get_env('DB_NAME', 'come_to_code_db'),
            'USER':     get_env('DB_USER', 'postgres'),
            'PASSWORD': get_env('DB_PASSWORD', 'postgres'),
            'HOST':     get_env('DB_HOST', 'localhost'),
            'PORT':     get_env('DB_PORT', '5432'),
        }
    }
        
# Sécurité automatique en production
if not DEBUG:
    # Hôtes autorisés en production
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
    CSRF_TRUSTED_ORIGINS = [
        f'https://{h.strip()}' for h in ALLOWED_HOSTS if h.strip() and h != '*'
    ]
    # Sécurité SSL / Cookies
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Stockage des fichiers statiques compressés avec Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    


AUTH_USER_MODEL = 'accounts.Apprenant'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DEFAULT_CHARSET='utf-8'
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Ouagadougou'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/tableau-de-bord/'
LOGOUT_REDIRECT_URL = '/'
