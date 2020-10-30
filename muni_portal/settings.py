"""
Django settings for muni_portal project.

Generated by 'django-admin startproject' using Django 2.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import environ

ROOT_DIR = environ.Path(__file__) - 2
PROJ_DIR = ROOT_DIR.path("muni_portal")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

env = environ.Env()

# GENERAL
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# Fail loudly if not set.
SECRET_KEY = env("DJANGO_SECRET_KEY")

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
# Rely on nginx to direct only allowed hosts, allow all for dokku checks to work.
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "muni_portal.core.apps.CoreConfig",
    "muni_portal.notifications.apps.NotificationsConfig",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "wagtail.api.v2",
    "modelcluster",
    "taggit",
    "rest_framework",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.core.middleware.SiteMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "muni_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["muni_portal/templates"],
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

WSGI_APPLICATION = "muni_portal.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = str(ROOT_DIR("staticfiles"))
STATIC_URL = "/static/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_DIRS = [
    str(PROJ_DIR.path("static")),
    str(ROOT_DIR.path("assets/bundles")),
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

WHITENOISE_AUTOREFRESH = env.bool("DJANGO_WHITENOISE_AUTOREFRESH", False)

MEDIA_ROOT = str(ROOT_DIR.path('development_media'))
MEDIA_URL = env.str("MEDIA_URL", '/media/')

import logging.config
import boto3


boto3.set_stream_logger("boto3.resources", logging.INFO)

LOGGING_CONFIG = None
logging.config.dictConfig(
    {
        "version": 1,
        # keep logs like django.server ERROR    "GET / HTTP/1.1" 500
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                # exact format is not important, this is the minimum information
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "console",},
        },
        "loggers": {
            # root logger
            "": {"level": "INFO", "handlers": ["console"],},
        },
    }
)


TAG_MANAGER_ENABLED = env.bool("TAG_MANAGER_ENABLED", True)
if TAG_MANAGER_ENABLED:
    TAG_MANAGER_CONTAINER_ID = env("TAG_MANAGER_CONTAINER_ID")


WAGTAIL_SITE_NAME = "Muni portal CMS"
WAGTAILAPI_BASE_URL = env.str("WAGTAILAPI_BASE_URL", None)

CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_FILE_STORAGE = env.str("DEFAULT_FILE_STORAGE", 'django.core.files.storage.FileSystemStorage')
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", None)
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", None)
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", None)
AWS_S3_SECURE_URLS = env.bool("AWS_S3_SECURE_URLS", True)
AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN", None)
# "S3Boto3Storage does not correctly handle duplicate filenames in their default configuration."
# https://docs.wagtail.io/en/v2.7.1/advanced_topics/deploying.html
AWS_S3_FILE_OVERWRITE = False
