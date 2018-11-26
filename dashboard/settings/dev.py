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

# dangerous on production
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST += [
    "localhost:3080",
    "localhost:4080",
    "dashboard-dev.ms.wits.ac.za:3080",
]

# makes life easier sometimes
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
]

# print annoying deprecated messages:
MIDDLEWARE = [
    # 'silk.middleware.SilkyMiddleware',
    'dashboard.shared.middleware.DeprecatedViewsMiddleware',
    *MIDDLEWARE,
]


# ========================================================================= #
# SILK - https://github.com/jazzband/django-silk                            #
# Annotate functions:         @silk_profile(name='Your Name')               #
# Context inside functions:   with silk_profile(name='Your Dynamic Name'):
# ========================================================================= #

from silk import auth

SILKY_PYTHON_PROFILER = True            # Use Python's built-in cProfile profiler to profile each request
SILKY_META = True                       # Record Silk's Impact

SILKY_MAX_REQUEST_BODY_SIZE = 1024      # Silk takes anything <0 as no limit
SILKY_MAX_RESPONSE_BODY_SIZE = 1024     # If response body>1024kb, ignore
SILKY_MAX_RECORDED_REQUESTS = 10000     # Max number of requests to store before garbage collection

# LOGIN_URL='^/admin/login'               <<< url works manually, but doesnt redirect correctly from /silk
# SILKY_AUTHENTICATION = True             # User must login, required: path('accounts/', include('django.contrib.auth.urls'))
# SILKY_AUTHORISATION = True              # User must have permissions (By default if is_staff)


# SILKY_PYTHON_PROFILER_BINARY = False  # If .prof files should be generated, and saved in the below path.
# SILKY_PYTHON_PROFILER_RESULT_PATH = os.path.join(DATA_DIR, 'profiling')
# SILKY_DYNAMIC_PROFILING = [
#     { # If we only have read only access to a library, same as annotating the function.
#         'module': 'path.to.module',
#         'function': 'MyClass.bar'
#     },
#     { # If we only have read only access to a library, same as using the context inside the function.
#         'module': 'path.to.module',
#         'function': 'MyClass.bar'
#         # Line numbers are relative to the function as opposed to the file in which it resides
#         'start_line': 1,
#         'end_line': 2,
#         'name': 'Slow Foo'
#     }
# ]
