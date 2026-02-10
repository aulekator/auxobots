from .base import *  # noqa: F403
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# Never use this default in production — it's only for quick local dev
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-!)r6%bjdaczwo^!$z_+3!e@&ii&zmkwdae_o3_t30p8k-09j*t",
)

# ALLOWED_HOSTS
# ------------------------------------------------------------------------------
# Add your local IPs and domain for development
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake", 
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # Insert at beginning

# Better panel config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
    # Optional: nicer toolbar positioning
    "INSERT_BEFORE": "</body>",
}

# Required for debug toolbar to show when accessing via IP or Docker
INTERNAL_IPS = [
    "127.0.0.1",
    "10.0.2.2",        # Android emulator
]

# EMAIL
# ------------------------------------------------------------------------------
# Console backend is perfect for local dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Optional: override default from email for clarity in console
DEFAULT_FROM_EMAIL = "AuxoBot Local Dev <auxobot@localhost>"

# django-extensions (great for shell_plus, runserver_plus, etc.)
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# anymail (for Sendinblue/Brevo) — keep it if you want real emails in local testing
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["anymail"]  # noqa: F405

ANYMAIL = {
    "SENDINBLUE_API_KEY": env("DJANGO_SENDINBLUE_API_KEY", default=""),
}

# Optional: Enable Django's built-in server logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}