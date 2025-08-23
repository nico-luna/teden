# Redirección al login manual
LOGIN_URL = '/login/'
# Configuración django-allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 4

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
import os
import logging
from pathlib import Path

# === BASE DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === SEGURIDAD ===
SECRET_KEY = 'django-insecure-_6v9pf)cpa_)rg^ia&yt9w=h@9=hb0(iqmhpk9fayx&_kdl!19'
DEBUG = True  # En producción siempre False
ALLOWED_HOSTS = [
    'teden.net',
    'teden.onrender.com',
    'localhost',
    '127.0.0.1',
    '.ngrok-free.app',  # Permite cualquier subdominio de ngrok
    "https://217.196.61.35",
]
# === APPS INSTALADAS ===
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://teden.net",
    "https://teden.onrender.com",
    "https://217.196.61.35",
    "https://*.ngrok-free.app",
]
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Allauth (eliminado para login manual)

    # Tus apps
    'users',
    'products',
    'core',
    'cart',
    'reviews',
    'store',
    'dashboard',
    'admin_panel',
    'orders',
    'payments',
    'appointments',

    # Utilidades
    'widget_tweaks',
    'cloudinary',
    'cloudinary_storage',
    'plans.apps.PlansConfig',
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',        # ← WhiteNoise aquí
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware para saltar el browser warning de ngrok
    'teden.ngrok_middleware.NgrokSkipBrowserWarningMiddleware',

    # Allauth (eliminado para login manual)
    # Cancelación automática de órdenes/citas no pagadas
    'core.middleware.auto_cancel.AutoCancelMiddleware',
]

# === URL & WSGI ===
ROOT_URLCONF = 'teden.urls'
WSGI_APPLICATION = 'teden.wsgi.application'

# === TEMPLATES ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# # === BASE DE DATOS ===

    


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'app',
#         'USER': 'app',
#         'PASSWORD': 'app',
#     'HOST': 'db',
#         'PORT': '5432',
#     }
# }
# === BASE DE DATOS ===
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"postgres://app:app@db:5432/app"),
        conn_max_age=600,
    )
}

# Compatibilidad: si corrés en Docker sin DATABASE_URL,
# sigue funcionando con el host `db`
if not os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "app",
            "USER": "app",
            "PASSWORD": "app",
            "HOST": "db",
            "PORT": "5432",
        }
    }



# === VALIDADORES DE CONTRASEÑA ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === LOCALIZACIÓN ===
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# === USUARIO ===
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# === EMAIL ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'joaco246810@gmail.com'
EMAIL_HOST_PASSWORD = 'pqnt dqbs ekvx abxf'
DEFAULT_FROM_EMAIL = 'joaco246810@gmail.com'

# === STATIC FILES ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# === MEDIA FILES (Cloudinary) ===
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dp2yymrpq',
    'API_KEY': '485295755515372',
    'API_SECRET': 'huDgtEeXRCHyOWDNTKyGBW_aA9Q',
}

# === MERCADOPAGO ===
SITE_URL = 'https://teden.net'

# === MercadoPago (hardcoded, sin .env) ===
MP_CLIENT_ID = "8320957227843622"
MP_CLIENT_SECRET = "l6P0hpO4NiYeGuYCkIsIDtdjZLcj9P2M"
MP_REDIRECT_URI = "https://teden.net/mercadopago/oauth/callback/"
MERCADOPAGO_ACCESS_TOKEN = "APP_USR-8320957227843622-082000-1589461840084336941202c0751a323a-1063624697"
MERCADOPAGO_PUBLIC_KEY = "APP_USR-6e30d21e-2695-414e-b68f-a891bfb5425c"
TEDEN_COLLECTOR_ID = 1063624697
MERCADOPAGO_CURRENCY_ID = 'USD'
APP_MARKETPLACE_ENABLED = True  # Cambia a False si no tienes Marketplace habilitado


# === PK POR DEFECTO ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG)
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.request': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
        'django.urls':   {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    }
}