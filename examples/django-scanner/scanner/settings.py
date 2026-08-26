from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "development-only-change-me"
DEBUG = True
# Include Django's test client host so the example is testable without
# weakening production host validation for real deployments.
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
ROOT_URLCONF = "scanner.urls"
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.middleware.common.CommonMiddleware"]
INSTALLED_APPS = ["django.contrib.staticfiles"]
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": []}}]
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "dist" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
