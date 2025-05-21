from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
from django.contrib.messages import constants as messages

load_dotenv(find_dotenv('.env'))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ctspms.apps.CtspmsConfig',
    'account.apps.AccountConfig',
    'chat.apps.ChatConfig',
    'fontawesomefree',
    'bootstrap5',
    'django_bootstrap_icons',
    'django_google_fonts',
    'ckeditor',
    'ckeditor_uploader',
    'cities_light',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
]


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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
ASGI_APPLICATION = 'config.asgi.application'

# If using Redis for Channels (recommended):
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

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

LANGUAGES = [
    ('af', 'Afrikaans'),
    ('ar', 'Arabic'),
    ('az', 'Azerbaijani'),
    ('bg', 'Bulgarian'),
    ('bn', 'Bengali'),
    ('ca', 'Catalan'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('en', 'English'),
    ('es', 'Spanish'),
    ('et', 'Estonian'),
    ('fa', 'Persian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('gu', 'Gujarati'),
    ('he', 'Hebrew'),
    ('hi', 'Hindi'),
    ('hr', 'Croatian'),
    ('hu', 'Hungarian'),
    ('id', 'Indonesian'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('kn', 'Kannada'),
    ('ko', 'Korean'),
    ('lt', 'Lithuanian'),
    ('lv', 'Latvian'),
    ('ml', 'Malayalam'),
    ('mr', 'Marathi'),
    ('my', 'Burmese'),
    ('nb', 'Norwegian Bokmål'),
    ('ne', 'Nepali'),
    ('nl', 'Dutch'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('pt-br', 'Brazilian Portuguese'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('sq', 'Albanian'),
    ('sr', 'Serbian'),
    ('sv', 'Swedish'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('th', 'Thai'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('vi', 'Vietnamese'),
    ('zh-hans', 'Simplified Chinese'),
    ('zh-hant', 'Traditional Chinese'),
]
TIME_ZONE = 'UTC'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'productionfiles'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth.User'

LOGIN_REDIRECT_URL = 'dashboard'  # Redirect to dashboard after login

# Redirect after logout
LOGOUT_REDIRECT_URL = 'login'  # Redirect to login page after logging out

# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
#
# SESSION_COOKIE_AGE = 5400 # 1.3-hours
#
# SESSION_COOKIE_HTTPONLY = True

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Looking to send emails in production? Check out our Email API/SMTP product!
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')


# CKEditor Settings
CKEDITOR_UPLOAD_PATH = 'upload/data/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format'],
            ['Bold', 'Italic', 'Underline'],  # Basic formatting options
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Image', 'Attachment', 'Table', 'HorizontalRule']
        ],
        'width': '100%',  # Set to 100% for responsive design
        'height': '300px',
        'removePlugins': 'sourcearea',  # Completely remove the Source button
        'extraPlugins': 'uploadimage',  # Add plugin for image upload
        'filebrowserUploadUrl': '/ckeditor/upload/',  # Specify the upload URL for images
        'filebrowserUploadMethod': 'form',  # Upload method (form-based)
    },
}