from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-9@y$ffa(s-k&z+t_4ce2zjp!!l(3oo=sm^$b0%3w6ve)ip@^q4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', ]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "service": "clapdb_pg",
            "passfile": "/Users/mwdiers/.pgpass",
        }
    }
}

