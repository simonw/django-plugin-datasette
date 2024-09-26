import djp
import tempfile
import os

tempdir = tempfile.TemporaryDirectory()
test_db = os.path.join(tempdir.name, "test.db")

SECRET_KEY = "django-insecure-test-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = []

MIDDLEWARE = []

ROOT_URLCONF = "tests.test_project.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": test_db,
        "TEST": {
            "NAME": test_db,
        },
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]

USE_TZ = True

djp.settings(globals())
