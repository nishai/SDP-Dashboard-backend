from typing import Dict, List

from django.db import models
from django.db.models import Model, QuerySet

# ========================================================================= #
# AGGREGATE METHODS                                                         #
# ========================================================================= #
from jsonschema import validate, ValidationError, SchemaError

AGGREGATE_METHODS = {
    "max": models.Max,
    "min": models.Min,
    "std": models.StdDev,
    "sum": models.Sum,
    "var": models.Variance,
    "ave": models.Avg,
    "count": models.Count,
}

# ========================================================================= #
# SCHEMA - https://json-schema.org & https://pypi.org/project/jsonschema    #
# ========================================================================= #


schema_filter = {
    "filter": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "comparator": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": [
                "field",
                "comparator",
                "value",
            ]
        },
        "uniqueItems": True,
        "minItems": 1,
    }
}

schema_group = {
    "type": "object",
    "properties": {
        "by": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "uniqueItems": True,
            "minItems": 1,
        },
        "yield": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "field name to generate",
                    },
                    "via": {
                        "enum": list(AGGREGATE_METHODS.keys()),
                        "description": "aggregate method",
                    },
                    "of": {
                        "type": "string",
                        "description": "field to apply aggregation to",
                    },
                },
                "required": [
                    # "name",
                    "via",
                    "of",
                ],
            },
            "uniqueItems": True,
            "minItems": 0,
        },
    },
    "required": [
        "by",
        "yield",
    ],
}

schema_order = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "field": {"type": "string"},
            "descending": {"type": "boolean"},
        },
        "required": [
            "field",
            "descending",
        ]
    },
    "uniqueItems": True,
    "minItems": 1,
}

schema_limit = {
    "type": "object",
    "properties": {
        "type": { # name, not type directive
            "enum": [
                "first",
                "last",
                "page",
            ]
        },
        "num": {
            "type": "integer",
        },
        "index": {
            "type": "integer"
        },
    },
    "required": [
        "type",
        "num",
    ]
}

# composite

schema_subquery = {
    "type": "object",
    "properties": {
        "filter": schema_filter,
        "group": schema_group,
        "order": schema_order,
        "limit": schema_limit,
    },
    # "required": [
    #     "limit"
    # ],
}

schema_query = {
    "type": "array",
    "items": schema_subquery,
    "minItems": 1,
    "maxItems": 1,  # TODO
    "uniqueItems": True,
}


# ========================================================================= #
# PARSERS                                                                   #
# ========================================================================= #


def _filter(queryset: QuerySet, fragment: Dict):
    return queryset


def _group(queryset: QuerySet, fragment: Dict):
    # find these unique pairs
    unique = queryset.values(*fragment['by'])
    # data generators
    yields = {}
    for y in fragment['yield']:
        (via, of) = (y['via'], y['of'])
        name = y['name'] if 'name' in y else f"{of}_{via}"
        yields[name] =  AGGREGATE_METHODS[via](of)
    # generate
    return unique.annotate(**yields)


def _order(queryset: QuerySet, fragment: List[Dict]):
    return queryset.order_by(*[
        (("-" + order['field']) if ('descending' in order and order['descending']) else order['field'])
        for order in fragment
    ])


def _limit(queryset: QuerySet, fragment: Dict[str, object]):
    (type, num) = fragment['type'], fragment['num']

    if type == 'page':
        i = fragment['index'] if 'index' in fragment else 0
        return queryset[max(0, i*num):min((i+1)*num, len(queryset))]
    elif type == 'first':
        return queryset[:min(num, len(queryset))]
    elif type == 'last':
        return queryset[max(0, len(queryset)-num):]


# TODO: check https://github.com/carltongibson/django-filter


def parse(model: Model, data: List):

    if data == {}:
        data = [data]

    try:
        validate(data, schema_query)
    except ValidationError as e:

        # TODO
        raise e
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    queryset = model.objects

    # https://www.laurencegellert.com/2016/09/django-group-by-having-query-example/
    for i, frag in enumerate(data):
        assert i == 0
        if 'group' not in frag:
            queryset = queryset.all()
            print(queryset)
        if 'filter' in frag:
            queryset = _filter(queryset, frag['filter'])
            print(queryset)
        if 'group' in frag:
            queryset = _group(queryset, frag['group'])
            print(queryset)
        if 'order' in frag:
            queryset = _order(queryset, frag['order'])
            print(queryset)
        # must contain limit
        queryset = _limit(queryset, frag['limit'] if 'limit' in frag else {"type": "first", "num": 10})

    return queryset
