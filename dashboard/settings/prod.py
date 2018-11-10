from .base import *


DEBUG = False

ALLOWED_HOSTS += ["dashboard-dev.ms.wits.ac.za"]


# ========================================================================= #
# CSRF (Cross-Site Request Forgery)                                         #
#                                                                           #
# Cross-Site Request Forgery (CSRF) is an attack that forces an end user to #
# execute unwanted actions on a web application in which they're currently  #
# authenticated. CSRF attacks specifically target state-changing requests,  #
# not theft of data, since the attacker has no way to see the response to   #
# the forged request. With a little help of social engineering (such as     #
# sending a link via email or chat), an attacker may trick the users of a   #
# web application into executing actions of the attacker's choosing. If the #
# victim is a normal user, a successful CSRF attack can force the user to   #
# perform state changing requests like transferring funds, changing their   #
# email address, and so forth. If the victim is an administrative account,  #
# CSRF can compromise the entire web application.                           #
# ========================================================================= #

CSRF_TRUSTED_ORIGINS = (
    'dashboard-dev.ms.wits.ac.za',
)

MIDDLEWARE += [
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]
