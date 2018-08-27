import os
logpath = os.path.join(os.path.abspath(os.path.join(__file__,os.path.join(*[os.pardir]*2))),"logs")

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
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'debug-import-file': {
            'level': 'DEBUG',
 #           'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
			'filename': logpath + '/debug_import.log',
			'maxBytes': 1024 * 1024 * 5, #5MB
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
		'debug-import': {
            'handlers': ['debug-import-file'],
            'level': 'DEBUG',
#            'filters': ['require_debug_true']
        }
    }
}

