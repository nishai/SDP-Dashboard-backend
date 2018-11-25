from django.conf.urls import url
from dashboard.apps.dash.views import *

# Urls
urlpatterns = [
    url(r'^status', status_view),   # Returns an empty body with status code 200 to check that the server is alive.
    url(r'^profile/data', profile_data_view), # needs to be above /profile
    url(r'^profile', profile_view),
    url(r'^user', user_view),
]
