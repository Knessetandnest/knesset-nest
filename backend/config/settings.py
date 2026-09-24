import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

DEBUG = env_bool("DEBUG", True)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
if not DEBUG and SECRET_KEY == "dev-only-change-me":
    raise RuntimeError("Set DJANGO_SECRET_KEY to a strong random value when DEBUG=False.")

ALLOWED_HOSTS = [x.strip() for x in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework", "core", "candidates",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":[
    "django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    p = urlparse(DATABASE_URL)
    DATABASES = {"default": {"ENGINE":"django.db.backends.postgresql","NAME":p.path.lstrip("/"),"USER":p.username,"PASSWORD":p.password,"HOST":p.hostname,"PORT":p.port or 5432,
                              "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
                              "CONN_HEALTH_CHECKS": True}}
else:
    DATABASES = {"default": {"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator","OPTIONS":{"min_length":10}},
    {"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE="en-us"; TIME_ZONE="Asia/Kolkata"; USE_I18N=True; USE_TZ=True
STATIC_URL="static/"; STATIC_ROOT=BASE_DIR / "staticfiles"
MEDIA_URL="/media/"; MEDIA_ROOT=BASE_DIR / os.getenv("MEDIA_ROOT","media")
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS=[x.strip() for x in os.getenv("CORS_ALLOWED_ORIGINS","http://localhost:5173").split(",") if x.strip()]
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS","http://localhost:5173").split(",") if x.strip()]
CORS_ALLOW_CREDENTIALS=True

SESSION_COOKIE_HTTPONLY=True
COOKIE_SAMESITE=os.getenv("COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_SAMESITE=COOKIE_SAMESITE
CSRF_COOKIE_SAMESITE=COOKIE_SAMESITE
CSRF_COOKIE_HTTPONLY=False
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_REFERRER_POLICY="same-origin"
X_FRAME_OPTIONS="DENY"

# Redis is used for production sessions/cache/throttling when REDIS_URL is set.
REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    try:
        import redis
        CACHES = {"default": {"BACKEND":"django.core.cache.backends.redis.RedisCache", "LOCATION":REDIS_URL}}
    except ImportError:
        raise RuntimeError("REDIS_URL is configured but redis is not installed.")
else:
    CACHES = {"default": {"BACKEND":"django.core.cache.backends.locmem.LocMemCache", "LOCATION":"knesset-nest-dev"}}

SESSION_ENGINE=os.getenv("SESSION_ENGINE", "django.contrib.sessions.backends.cached_db")
SESSION_CACHE_ALIAS="default"

REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES":["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_CLASSES":[
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES":{"anon":"60/minute", "user":"600/minute"},
    "DEFAULT_RENDERER_CLASSES":["rest_framework.renderers.JSONRenderer"],
}

DATA_UPLOAD_MAX_MEMORY_SIZE=6*1024*1024
FILE_UPLOAD_MAX_MEMORY_SIZE=6*1024*1024

# Optional S3-compatible object storage for production resumes.
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
if AWS_STORAGE_BUCKET_NAME:
    INSTALLED_APPS.append("storages")
    STORAGES = {
        "default": {"BACKEND":"storages.backends.s3.S3Storage", "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": os.getenv("AWS_S3_REGION_NAME", ""),
            "endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL", "") or None,
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "default_acl": None,
            "querystring_auth": True,
        }},
        "staticfiles": {"BACKEND":"whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND":"django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND":"whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

if env_bool("SECURE_COOKIES", False):
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
    SECURE_SSL_REDIRECT=True
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS=int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True
    SECURE_HSTS_PRELOAD=True
