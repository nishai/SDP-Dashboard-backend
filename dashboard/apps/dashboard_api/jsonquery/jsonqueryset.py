from pprint import pprint
from typing import Type
from django.db.models import Model
from jsonschema import validate, ValidationError, SchemaError
from dashboard.apps.dashboard_api.jsonquery import actions


# ========================================================================= #
# REQUEST HANDLERS                                                          #
# ========================================================================= #
from dashboard.apps.dashboard_api.management.util.modelinfo import ModelInfo


def parse_request(model: Type[Model], data: dict, fake=False):
    try:
        validate(data, actions.SCHEMA)
    except ValidationError as e:
        raise e
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    queryset = set(f.name for f in model._meta.get_fields()) if fake else (model.objects.all().values())

    if 'query' in data and len(data['query']) > 0:
        for i, fragment in enumerate(data['query']):
            action = actions.ACTIONS[fragment['action']]
            queryset = action.fake(model, queryset, fragment) if fake else action.handle(queryset, fragment)

    return queryset


def parse_options(model: Type[Model], data: dict):
    return set(ModelInfo.static_generate_query_tree(model)) | set(parse_request(model, data, fake=True))
