
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
import dj_database_url
import os
from tempfile import NamedTemporaryFile
import firebase_admin
from firebase_admin import credentials
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True


SECRET_KEY = config('SECRET_KEY','change moi vite')
DEBUG = True
config('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = [config('RENDER_EXTERNAL_HOSTNAME'),'127.0.0.1','localhost', '10.193.17.188']





# Celery config
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_TIMEZONE = 'Africa/Dakar'

# # Celery Beat Scheduler
# CELERY_BEAT_SCHEDULE = {
#     'envoyer-notifications-culture': {
#         'task': 'notifications.tasks.envoyer_notifications_culture',
#         'schedule': crontab(hour=19, minute=30),
#     },
# }


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #Applications locales
    'farm_management',
    'users',
    'parcelle',

    #applications pour l'authentification
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    #'django_rest_passwordreset',
    'corsheaders', 
    # Celery
    'django_celery_beat',
    'fcm_django',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    
]

#firebase 







# # Lire la variable d'environnement qui contient tout le JSON
firebase_credentials_json = config('FIREBASE_CREDENTIALS_JSON')

if firebase_credentials_json:
    # Crée un fichier temporaire contenant le JSON
    with NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        temp_file.write(firebase_credentials_json.encode('utf-8'))
        temp_file.flush()

        # Initialise Firebase Admin avec ce fichier temporaire
        cred = credentials.Certificate(temp_file.name)
        firebase_admin.initialize_app(cred)

else:
    raise Exception("La variable d'environnement FIREBASE_CREDENTIALS_JSON est manquante")





MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]
CORS_ALLOW_ALL_ORIGINS=True
ROOT_URLCONF = 'sukeliagri_back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sukeliagri_back.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}





# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'

# Dossier où collectstatic va copier tous les fichiers statiques pour production
STATIC_ROOT = BASE_DIR / 'staticfiles'

AUTH_USER_MODEL = 'users.CustomUser'



OPENWEATHER_API_KEY = '3b60796360b908aa07979df70b9afc08'
WEATHERAPI_API_KEY = 'a51afd7896fe45609ea213346250901'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=180),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_USER_CLASS': 'userapp.CustomUser',

}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'SUKKELAGRI <noreply@sukelagri.com>'



##################################################################################################################################
######################    Settings pour python anywhere  ########################################################



# Configuration Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


