from pathlib import Path

import dj_database_url
from decouple import config



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")

ENVIRONMENT = config("ENVIRONMENT", default="production")

POSTGRES_LOCALLY = config("POSTGRES_LOCALLY", default=False, cast=bool)

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)


if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=lambda v: v.split(","))

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=lambda v: v.split(","))

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "cloudinary_storage",
    "cloudinary",
    "administrators.apps.AdministratorsConfig",
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

if ENVIRONMENT == "production" or ENVIRONMENT == "stagging" or POSTGRES_LOCALLY is True:
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
MEDIA_URL = "/media/"

if ENVIRONMENT == "development":
    MEDIA_ROOT = BASE_DIR / "media"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Serve static files during development with cloudinary
if ENVIRONMENT == "production" or ENVIRONMENT == "stagging":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
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

# Session Settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Add after AUTHENTICATION_BACKENDS
AUTH_USER_MODEL = "auth.User"

# Configure email as required field
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "email"

# Email settings
if ENVIRONMENT == "production":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 465
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = f"DuesFlow <{config('DEFAULT_FROM_EMAIL')}>"
    CONTACT_EMAIL_1 = config("CONTACT_EMAIL_1")
    CONTACT_EMAIL_2 = config("CONTACT_EMAIL_2")
    CONTACT_EMAIL_3 = config("CONTACT_EMAIL_3")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST_USER = "test@example.com"
    DEFAULT_FROM_EMAIL = "DuesFlow <test@example.com>"
    CONTACT_EMAIL_1 = "contact1@example.com"
    CONTACT_EMAIL_2 = "contact2@example.com"
    CONTACT_EMAIL_3 = "contact3@example.com"

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "debug.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "a_home": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

JAZZMIN_SETTINGS = {
    # General settings
    "site_title": "DuesFlow Admin",
    "site_header": "DuesFlow",
    "site_brand": "DuesFlow",
    "site_logo": "images/logo.svg",
    "welcome_sign": "Welcome to DuesFlow Administration",
    "copyright": "Nesttop Technologies Ltd",
    # Top Menu items
    "topmenu_links": [
        {"name": "Home", "url": "home", "permissions": ["auth.view_user"]},
        {
            "name": "Departments",
            "url": "students:department_list",
            "permissions": ["auth.view_user"],
        },
        {"model": "students.Student"},
        {"model": "payments.Payment"},
    ],
    # UI Customizer
    "show_ui_builder": True,
    # Theme settings
    "dark_mode_theme": False,
    "brand_colour": "blue",
    "accent": "accent",
    "brand_icon": "fas fa-graduation-cap",
    # Custom CSS/JS
    "custom_css": "css/custom_admin.css",
    "custom_js": None,
    # Hide logo on login page
    "hide_logo_on_login": True,
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "students.Student": "fas fa-user-graduate",
        "students.Department": "fas fa-building",
        "payments.Payment": "fas fa-money-bill-wave",
        "administrators.CustomUser": "fas fa-user-shield",
        "administrators.DepartmentAdmin": "fas fa-user-tie",
        "students.PendingMomoPayment": "fas fa-money-check-alt",
    },
    # Cards
    "show_ui_builder": False,
    # Related Modal
    "related_modal_active": False,  # Change this to False
    # Show foreign keys as raw ID fields
    "show_foreign_keys": True,
    # Change foreign key representation
    "foreign_keys_format": "raw_id",
    # Add base URL for links
    "site_url": "/",
    # Configure changeform template
    "changeform_format": "horizontal_tabs",
    # Custom Links
    "custom_links": {
        "students": [
            {
                "name": "View Departments",
                "url": "students:department_list",
                "icon": "fas fa-building",
            }
        ]
    },
    # Order with respect to model icons
    "order_with_respect_to": ["auth", "students", "payments"],
    # Theme colors
    "theme": {
        "primary": "blue",
        "secondary": "indigo",
        "accent": "purple",
        "navbar": "bg-gradient-to-r from-blue-600 to-indigo-600",
        "darkness": False,
    },
}

# Additional Jazzmin UI settings
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY")

DEYWURO_USERNAME = config("DEYWURO_USERNAME")
DEYWURO_PASSWORD = config("DEYWURO_PASSWORD")
DEYWURO_SOURCE = config("DEYWURO_SOURCE")
