# ========================================================================= #
# Django pytest Documentation:                                              #
#     - https://pytest-django.readthedocs.io/en/latest/helpers.html         #
#                                                                           #
# Functions that start with "test_" are pytest tests.                       #
#   - 'Arguments' to test functions are called fixtures and are generated   #
#     by pytest on the fly based on their name.                             #
#   - You can define a new fixture by annotating a function with            #
#     @pytest.fixture (The name of the func corresponds to args in a test)  #
#   - Default fixtures are defined by django-pytest... see the link above   #
# ========================================================================= #

import pytest


# def test_endpoint_status(client):
#     assert client.get('/status').status_code == 200

@pytest.mark.django_db
def test_endpoint_auth_token_obtain(client):
    assert client.post('/auth/token/obtain', {'username': 'user', 'password': 'pass'}).status_code == 400

@pytest.mark.django_db
def test_endpoint_auth_token_refresh(client):
    assert client.post('/auth/token/refresh', {'token': 'invalid_token'}).status_code == 400
