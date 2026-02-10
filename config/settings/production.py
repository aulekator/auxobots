from .base import *  # noqa: F403
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = False 

# SECURITY WARNING: Must be set via env var – never hardcode in production!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# ALLOWED_HOSTS – Use env var for flexibility (e.g., multiple domains/subdomains)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["auxobots.com", "www.auxobots.com"])

# DATABASE
# ------------------------------------------------------------------------------
DATABASES["default"] = env.db("DATABASE_URL")

DATABASES["default"]["CONN_MAX_AGE"] = 60          # good choice

DATABASES["default"]["OPTIONS"] = {
    "init_command": (
        "SET SESSION MAX_EXECUTION_TIME = 30000; "     # 30 seconds
        "SET sql_mode='STRICT_TRANS_TABLES'; "
        "SET innodb_strict_mode=1;"
    ),
    "connect_timeout": 30,
}

DATABASES["default"]["ATOMIC_REQUESTS"] = False     # good for trading/long-running tasks

# CACHES – Better to use env var (in case you scale to Redis or external Memcached)
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake-for-auxobot",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000
        }
    }
}

# SECURITY SETTINGS – Strongly recommended for production HTTPS sites
# ------------------------------------------------------------------------------
# If behind a reverse proxy (Nginx, Traefik, etc.) that terminates SSL:

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS – Start with 1 year once HTTPS is stable
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # Deprecated in modern browsers but harmless
X_FRAME_OPTIONS = "DENY"  # Or "SAMEORIGIN" if you use iframes

# TEMPLATES – Use cached loader for better performance
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# ADMIN
# ------------------------------------------------------------------------------
ADMIN_URL = env("DJANGO_ADMIN_URL")  # Keep random/secret

# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="auxobot <auxobot@auxobot.com>")
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = "[auxobot] "

# Use Anymail/Sendinblue for production sending
EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

# LOGGING – Fixed duplicates, better structure, and production-friendly
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        }
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "file": {
            "level": "INFO",  # INFO or WARNING in prod – DEBUG creates huge files
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/django/auxobot.log",  # Adjust path as needed
            "maxBytes": 1024 * 1024 * 100,  # 100 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"],
    },
    "loggers": {
        "django.request": {
            "level": "ERROR",
            "handlers": ["file", "mail_admins"],
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["file", "mail_admins"],
            "propagate": False,
        },
    },
}

# ANYMAIL
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["anymail"]  # noqa: F405

ANYMAIL = {
    "SENDINBLUE_API_KEY": env("DJANGO_SENDINBLUE_API_KEY"),
}