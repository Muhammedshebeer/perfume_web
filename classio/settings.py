import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-change-me-before-deployment-classio-2026'
    else:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY for production.')
ALLOWED_HOSTS = [s.strip() for s in os.getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',') if s.strip()]
CSRF_TRUSTED_ORIGINS = [s.strip() for s in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if s.strip()]
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages','django.contrib.staticfiles',
    'shop.apps.ShopConfig',
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
ROOT_URLCONF = 'classio.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR/'templates'], 'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'shop.context_processors.cart_summary',
    ]},
}]
WSGI_APPLICATION = 'classio.wsgi.application'
ASGI_APPLICATION = 'classio.asgi.application'
DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME': BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = [
 {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE='en-us'
TIME_ZONE='Asia/Dubai'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
STORAGES = {
    'default': {'BACKEND':'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='dashboard'
LOGOUT_REDIRECT_URL='home'
MAX_PRODUCT_IMAGE_MB = int(os.getenv('MAX_PRODUCT_IMAGE_MB', '5'))
DATA_UPLOAD_MAX_MEMORY_SIZE=30 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE=5 * 1024 * 1024
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
X_FRAME_OPTIONS='DENY'
if not DEBUG:
    SECURE_SSL_REDIRECT=os.getenv('DJANGO_SECURE_SSL_REDIRECT','True').lower()=='true'
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
    SECURE_HSTS_SECONDS=31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True
    SECURE_HSTS_PRELOAD=True
    SECURE_CONTENT_TYPE_NOSNIFF=True
