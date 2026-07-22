from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'nucleo_new'),
        'USER': os.environ.get('POSTGRES_USER', 'nucleo'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'nucleo'),
        'HOST': 'db',
        'PORT': 5432,
    }
}