from pathlib import Path

from decouple import config

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("DJANGO_SECRET_KEY")

ENVIRONMENT = config("ENVIRONMENT", default="production")

POSTGRES_LOCALLY = config("POSTGRES_LOCALLY", default=False, cast=bool)

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
print(DEBUG)

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["dues-colleection-saas-app.onrender.com", "localhost:8000", "127.0.0.1:8000"]


INSTALLED_APPS = [
    # 'jazzmin',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "administrators.apps.AdministratorsConfig",  # or just 'administrators'
    "a_home",
    "students",
    "payments",
    "widget_tweaks",
    "admin_honeypot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "administrators.middleware.CustomUserMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if ENVIRONMENT == "production" or POSTGRES_LOCALLY is True:
    DATABASES["default"] = dj_database_url.parse(config("DATABASE_URL"))

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Serve static files during development with cloudinary
if ENVIRONMENT == "production":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

# Login/Logout Settings
LOGIN_URL = "administrators:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "administrators:login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "administrators.auth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Add after AUTHENTICATION_BACKENDS
AUTH_USER_MODEL = "auth.User"

# Configure email as required field
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "email"

# JAZZMIN_SETTINGS = {
#     "site_title": "DuesFlow",
#     "site_header": "DuesFlow Admin",
#     "site_brand": "DuesFlow",
#     "site_logo": "/images/logo.svg",
#     "welcome_sign": "Welcome to DuesFlow Admin",
#     "search_model": "students.Student",
#     "copyright": "Nesttop Technologies Ltd",
#     "topmenu_links": [
#         {"name": "Home", "url": "a_home:home", "permissions": ["auth.view_user"]},
#         {"name": "Students", "url": "admin:students_student_changelist", "permissions": ["students.view_student"]},
#         {"name": "Payments", "url": "admin:payments_payment_changelist", "permissions": ["payments.view_payment"]},
#     ]

# }
# JAZZMIN_SETTINGS["show_ui_builder"] = True
