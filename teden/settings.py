from pathlib import Path
import os

# === BASE DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent


# === SEGURIDAD ===
SECRET_KEY = 'django-insecure-_6v9pf)cpa_)rg^ia&yt9w=h@9=hb0(iqmhpk9fayx&_kdl!19'
DEBUG = True  # ⚠️ Desactivar en producción
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'teden.onrender.com']


# === APPS INSTALADAS ===
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Sitio y cuentas (allauth)
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Apps personalizadas
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
    'plans',
    # Utilidades
    'widget_tweaks',
    'cloudinary',
    'cloudinary_storage',
]


# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware de allauth
    'allauth.account.middleware.AccountMiddleware',
]


# === URLS & WSGI ===
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


# === BASE DE DATOS ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# === VALIDADORES DE CONTRASEÑA ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# === CONFIGURACIÓN REGIONAL ===
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True


# === USUARIO PERSONALIZADO ===
AUTH_USER_MODEL = 'users.User'


# === STATIC FILES ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# === MEDIA FILES ===
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# === CLOUDINARY ===
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dp2yymrpq',
    'API_KEY': '485295755515372',
    'API_SECRET': 'huDgtEeXRCHyOWDNTKyGBW_aA9Q',
}


# === AUTENTICACIÓN ===
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    # Si activás allauth, descomentá esta línea:
    # 'allauth.account.auth_backends.AuthenticationBackend',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# === EMAIL ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'joaco246810@gmail.com'
EMAIL_HOST_PASSWORD = 'pqnt dqbs ekvx abxf'  # ⚠️ Usar variables de entorno en producción
DEFAULT_FROM_EMAIL = 'joaco246810@gmail.com'


# === MERCADOPAGO ===
MP_CLIENT_ID = os.getenv("MP_CLIENT_ID")
MP_CLIENT_SECRET = os.getenv("MP_CLIENT_SECRET")
MP_REDIRECT_URI = "https://teden.com/oauth/mercadopago/callback/"
MERCADOPAGO_ACCESS_TOKEN = 'TEST-3479281247201721-061619-ed800695334c87adde3970f868bce658-488351234'


# === STRIPE ===
STRIPE_SECRET_KEY = 'tu_secret_key'


# === ID POR DEFECTO PARA PRIMARY KEY ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'