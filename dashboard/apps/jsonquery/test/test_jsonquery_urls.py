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

from dashboard.apps.jsonquery.models import EnrolledCourse, Course
from dashboard.apps.jsonquery.parser.jsonqueryset import register_action, parse_request, parse_options, QuerysetAction, ACTIONS
from dashboard.shared.errors import VisibleError


def test_jsonqueryset_register_action():
    # must succeed
    @register_action
    class FilterActionYes(QuerysetAction):
        name = 'test_action'
        properties = {}

    # must fail, already registered under same name.
    with pytest.raises(Exception):
        @register_action
        class FilterActionNo(QuerysetAction):
            name = 'test_action'
            properties = {}


data = {
    "queryset": [
        {
            "action": "order_by",
            "fields": [
                {
                    "field": "asdf",
                    "descending": True
                }
            ]
        },
        {
            "action": "limit",
            "method": "first",
            "num": 2
        },
        {
            "action": "values",
            "fields": [
                  "course_code",
                    "enrolled_year_id__progress_outcome_type"
            ]
        },
        {
            "action": "annotate",
            "fields": [
                {
                    "field": "asdf",
                    "expr": "max('final_mark')"
                },
                {
                    "field": "year",
                    "expr": "F('enrolled_year_id__calendar_instance_year')"
                }
            ]
        },
        {
            "action": "distinct"
        },
        {
            "action": "reverse"
        },
        {
            "action": "all"
        },
        {
            "action": "none"
        },
        {
            "action": "filter",
            "fields": [
                {
                    "field": "final_mark",
                    "expr": "F('final_mark') < 5"
                }
            ]
        },
        {
            "action": "exclude",
            "fields": [
                {
                    "field": "final_mark",
                    "expr": "F('final_mark') > 5"
                }
            ]
        },
        {
            "action": "values_list"
        },
        {
            "action": "limit",
            "method": "first",
            "num": 10
        }
    ]
}

@pytest.mark.django_db
def test_endpoint_data_courses_post(admin_client):
    assert admin_client.post('/data/courses?fake=0', data).status_code == 301
    assert admin_client.post('/data/courses/?fake=0', data).status_code == 405
    # TODO, not being sent properly


@pytest.mark.django_db
def test_endpoint_data_courses_post_fake(admin_client):
    assert admin_client.post('/data/courses?fake=1', data).status_code == 301
    assert admin_client.post('/data/courses/?fake=1', data).status_code == 405
    # TODO, not being sent properly


@pytest.mark.django_db
def test_endpoint_data_courses_options(admin_client):
    assert admin_client.options('/data/courses', data).status_code == 301
    assert admin_client.options('/data/courses/', data).status_code == 200
    # TODO, not being sent properly


@pytest.mark.django_db
def test_jsonqueryset_action(admin_client):
    for action in data['queryset']:
        with pytest.raises(Exception):
            ACTIONS[action['action']].fake(set(), action)
            raise Exception
        with pytest.raises(Exception):
            ACTIONS[action['action']].handle(Course.objects.values(), action)
            raise Exception
