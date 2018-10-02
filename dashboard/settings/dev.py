from .base import *


DEBUG = True
ALLOWED_HOSTS += ['*']

INSTALLED_APPS += [
    # erd diagram generator
    #'django_extensions',
]

# graph generation
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
