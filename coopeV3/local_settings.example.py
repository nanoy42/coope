# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Your secret key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['Server ip']

# Admins

ADMINS = []

EMAIL_HOST = ""

SERVER_EMAIL = ""


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
