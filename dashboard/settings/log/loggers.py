

def create_default_logger(log_path, name):

    # template from django docs:
    # https://docs.djangoproject.com/en/2.1/topics/logging/
    # and django loggers and handlers
    # https://stackoverflow.com/questions/45972977/django-logging-requests

    logger = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{asctime} | {levelname:8s} {module:12s} | {message}',
                'style': '{',
            },
            'simple': {
                'format': '{asctime} | {levelname:8s} | {message}',
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
                #            'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'debug-import-file': {
                'level': 'DEBUG',
                #           'filters': ['require_debug_true'],
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': log_path + '/debug_import/' + name + '.log',
                'maxBytes': 1024 * 1024 * 5,  # 5MB
            },
            'django-record': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': log_path + '/django_record/' + name + '.log',
            },
            'django-request-error': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': log_path + '/django_request_errors/' + name + '.log',
            },
            'django-db-error': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': log_path + '/django_db_error/' + name + '.log',
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
                'handlers': ['debug-import-file', 'console'],
                'level': 'DEBUG',
                #            'filters': ['require_debug_true']
            }
        }
    }

    import os

    def make_all_dirs(paths):
        for path in paths:
            if not os.path.isdir(path):
                os.makedirs(path)
                print(f"Made Directory: {path}")

    make_all_dirs([os.path.dirname(h['filename']) for h in logger['handlers'].values() if 'filename' in h])

    return logger
