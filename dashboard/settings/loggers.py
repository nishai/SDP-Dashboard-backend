# template from django docs:
# https://docs.djangoproject.com/en/2.1/topics/logging/
# and django loggers and handlers
# https://stackoverflow.com/questions/45972977/django-logging-requests

import os
import datetime
LOG_PATH = os.path.join(os.path.abspath(os.path.join(__file__,os.path.join(*[os.pardir]*3))),"logs")
CURR_TIME = str(datetime.datetime.now()).replace(" ","_").replace(":","").replace("-","")[:-7]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
#            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'debug-import-file': {
            'level': 'DEBUG',
 #           'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
	    'filename': LOG_PATH + '/debug_import/' + CURR_TIME + '.log',
	    'maxBytes': 1024 * 1024 * 5, #5MB
        },
	'django-record': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_PATH + '/django_record/' + CURR_TIME + '.log',
        },
	'django-request-error': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_PATH + '/django_request_errors/' + CURR_TIME + '.log',
        },
	'django-db-error': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_PATH + '/django_db_error/' + CURR_TIME + '.log',
        },
    },
    'loggers': {
            'django': {
            'handlers': ['django-record', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['django-request-error', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['django-db-error', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
	'debug-import': {
            'handlers': ['debug-import-file'],
            'level': 'DEBUG',
#            'filters': ['require_debug_true']
        }
    }
}

