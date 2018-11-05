import os

if os.environ.get("DJANGO_DEVELOP") == "true":
    from .dev import *
else:
    from .prod import *

# override the default database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.test.sqlite3'),
        'OPTIONS': {
            'timeout': 10,  # https://docs.python.org/3.7/library/sqlite3.html#sqlite3.connect
        }
    }
}
