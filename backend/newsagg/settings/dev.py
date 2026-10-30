# newsagg/settings/dev.py

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

#CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "newsagg"),
        "USER": os.getenv("POSTGRES_USER", "newsagg"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "newsagg22"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),  #localhost
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# --------------------
# Redis URLs
# --------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", "0")
REDIS_BROKER_DB = os.getenv("REDIS_BROKER_DB", "1")
REDIS_RESULT_DB = os.getenv("REDIS_RESULT_DB", "2")

REDIS_CACHE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}"
REDIS_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}"
REDIS_RESULT_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULT_DB}"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_CACHE_URL,                             #os.getenv("REDIS_URL0", "redis://redis:6379/0"),   #localhost
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

#CELERY_BROKER_URL = os.getenv("REDIS_URL1", "redis://redis:6379/1")  #localhost
#CELERY_RESULT_BACKEND = os.getenv("REDIS_URL2", "redis://redis:6379/2")  #localhost
# --------------------
# Celery
# --------------------
CELERY_BROKER_URL = REDIS_BROKER_URL
CELERY_RESULT_BACKEND = REDIS_RESULT_URL

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"