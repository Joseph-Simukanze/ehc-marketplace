import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'django.contrib.auth',
    # Third party apps
    'channels',  # For WebSockets
    'crispy_forms',  # For forms
    'crispy_bootstrap5',  # Bootstrap 5 for forms
    
    # Local apps
    'accounts',
    'marketplace',
    'payments',
    'reports',
    'chatbot',
    'chat',
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

ROOT_URLCONF = 'ehc_marketplace.urls'

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

WSGI_APPLICATION = 'ehc_marketplace.wsgi.application'
ASGI_APPLICATION = 'ehc_marketplace.asgi.application'

# Channel layers for WebSockets
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lusaka'  # Zambia timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URL
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'marketplace/home'

# Payment gateway API keys
MTN_API_KEY = os.environ.get('MTN_API_KEY', '')
MTN_API_SECRET = os.environ.get('MTN_API_SECRET', '')
MTN_API_URL = os.environ.get('MTN_API_URL', 'https://api.mtn.com')

AIRTEL_API_KEY = os.environ.get('AIRTEL_API_KEY', '')
AIRTEL_API_SECRET = os.environ.get('AIRTEL_API_SECRET', '')
AIRTEL_API_URL = os.environ.get('AIRTEL_API_URL', 'https://api.airtel.com')

# Google Maps API key for location services
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Subscription settings
MONTHLY_SUBSCRIPTION_AMOUNT = float(os.environ.get('MONTHLY_SUBSCRIPTION_AMOUNT', '50.0'))

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Using Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yourgmail@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your_app_password'  # Your Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = 'yourgmail@gmail.com'  # Where you want to receive contact messages

# settings.py

# settings.py

LOGIN_URL = '/accounts/login/'  # <-- Correct path based on your URL patterns

# settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key securely from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# settings.py

import os

STRIPE_TEST_SECRET_KEY = os.getenv("STRIPE_TEST_SECRET_KEY")
STRIPE_TEST_PUBLISHABLE_KEY = os.getenv("STRIPE_TEST_PUBLISHABLE_KEY")

from decouple import config

MTN_PRIMARY_KEY = config('MTN_PRIMARY_KEY')
MTN_SECONDARY_KEY = config('MTN_SECONDARY_KEY')


MTN_PRIMARY_KEY = '1Lbrx4Lx3hEreTuYXZUsH11XTZfnGS3njG'
MTN_BASE_URL = 'https://sandbox.momodeveloper.mtn.com'

# settings.py
MTN_SUBSCRIPTION_KEY = "your_subscription_key"
MTN_API_USER = "your_base64_encoded_user"
MTN_API_KEY = "your_api_key"

# Twilio settings
TWILIO_ACCOUNT_SID = 'ACb27d7595ffdc02e7cf697ce382d25201'
TWILIO_AUTH_TOKEN = '573e3e52a99acd63b5f03e53afeb8ad0'
TWILIO_VERIFY_SERVICE_SID = 'VAa2560f15d44d44e5df544edb303da800'
