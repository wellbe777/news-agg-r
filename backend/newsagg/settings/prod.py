# newsagg/settings/prod.py

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    os.getenv("DJANGO_ALLOWED_HOST", "localhost"),
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL", "http://localhost"),
]


# Postgres container from docker-compose
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),   #postgres
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}
"""

# Redis container from docker-compose
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/0",
    }
}

CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = "redis://redis:6379/2"

# Static file serving (for nginx)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
