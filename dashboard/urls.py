"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import url, include


urlpatterns = [
    # AUTH: JWT Authentication TODO: THIS IS NOT SECURE UNTIL HTTPS IS USED
    # http://getblimp.github.io/django-rest-framework-jwt
    url(r'^auth/token/obtain', obtain_jwt_token),     # obtain a new token from user + pass
    url(r'^auth/token/refresh', refresh_jwt_token),   # obtain a new token from an old token : JWT_ALLOW_REFRESH=True

    # DOCS: Third Party Documentation / Profiling
    url(r'^swag/', get_swagger_view(title='Wits Dashboard Api')),
    url(r'^silk/', include('silk.urls', namespace='silk')),

    # DOCS: Builtin Django database admin
    path('admin/', admin.site.urls),
]


# api
urlpatterns += [
    url(r'^', include('dashboard.apps.dash.urls')),
    url(r'^', include('dashboard.apps.wits.urls')),
]
