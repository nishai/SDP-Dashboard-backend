from typing import Dict, List, Type
from django.db import models
from django.db.models import Model, QuerySet, Q
from functools import reduce

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
                "operator": {"type": "string"},
                "value": {"type": "array"},
                "exclude": {"type": "boolean"},  # default to false
            },
            "required": [
                "field",
                "operator",
                "value",
            ],
        },
        "uniqueItems": True,
        "minItems": 0,
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
                    "from": {
                        "type": "string",
                        "description": "field to apply aggregation to",
                    },
                },
                "required": [
                    # "name",
                    "via",
                    "from",
                ],
            },
            "uniqueItems": True,
            "minItems": 0,
        },
    },
    "required": [
        "by",
        # "yield",
    ],
}

schema_order = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "field": {"type": "string"},
            "descending": {"type": "boolean"},  # defaults to false
        },
        "required": [
            "field"
        ]
    },
    "uniqueItems": True,
    "minItems": 0,
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
    },
}

schema_query = {
    "type": "object",
    "properties": {
        "chain": {
            "type": "array",
            "items": schema_subquery,
            "minItems": 0,
            "uniqueItems": True,
        },
        "limit": schema_limit
    }
}


# ========================================================================= #
# PARSERS                                                                   #
# ========================================================================= #


def _filter(queryset: QuerySet, fragment: List):
    for f in fragment:
        if 'exclude' not in f:
            f['exclude'] = False
        filterer = (queryset.exclude if f['exclude'] else queryset.filter)
        if len(f['value']) != 0:
            qValues = [Q(**{f"{f['field']}__{f['operator']}": value}) for value in f['value']]
            queryset = filterer(reduce(lambda a,b: a | b, qValues))
        else:
            print("FUTURE PROBLEMS, FIX ME IN THE JSON VALIDATION ABOVE")
    return queryset


def _group(queryset: QuerySet, fragment: Dict):
    # find these unique pairs
    unique = queryset.order_by(*fragment['by']).values_list(*fragment['by'], flat=True).distinct()
    # return early
    if 'yield' not in fragment:
        fragment['yield'] = []
    # data generators
    yields = {}
    for y in fragment['yield']:
        (_via, _from) = (y['via'], y['from'])
        name = y['name'] if 'name' in y else f"{_from}_{_via}"
        yields[name] =  AGGREGATE_METHODS[_via](_from)
    # generate
    return unique.annotate(**yields)


def _order(queryset: QuerySet, fragment: List[Dict]):
    return queryset.order_by(*[
        (("-" + order['field']) if ('descending' in order and order['descending']) else order['field'])
        for order in fragment
    ])


def _limit(queryset: QuerySet, fragment: Dict[str, object]):
    (type, num) = fragment['type'], fragment['num']

    if num == -1:
        return queryset

    if type == 'page':
        i = fragment['index'] if 'index' in fragment else 0
        return queryset[max(0, i*num):min((i+1)*num, len(queryset))]
    elif type == 'first':
        return queryset[:min(num, len(queryset))]
    elif type == 'last':
        return queryset[max(0, len(queryset)-num):]

def parse(model: Type[Model], data: Dict):

    try:
        validate(data, schema_query)
    except ValidationError as e:
        raise e
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    queryset = model.objects.all().values()

    if 'chain' in data and len(data['chain']) > 0:
        # https://www.laurencegellert.com/2016/09/django-group-by-having-query-example/
        for i, frag in enumerate(data['chain']):
            if 'group' not in frag:
                queryset = queryset.all()
            if 'filter' in frag:
                queryset = _filter(queryset, frag['filter'])
            if 'group' in frag:
                queryset = _group(queryset, frag['group'])
            if 'order' in frag:
                queryset = _order(queryset, frag['order'])
    else:
        queryset = queryset.all()

    queryset = _limit(queryset, data['limit'] if 'limit' in data else {"type": "first", "num": -1})

    return queryset


# TODO: check https://github.com/carltongibson/django-filter

# Valid Query Example:

# {
# 	"chain": [
# 		{
# 			"group": {
# 				"by": [
# 					"age",
# 					"race_description"
# 				],
# 				"yield": [
# 					{
# 						"name": "ave",
# 						"via": "ave",
# 						"from": "average_marks"
# 					},
# 					{
# 						"name": "count",
# 						"via": "count",
# 						"from": "average_marks"
# 					}
# 				]
# 			},
# 			"order": [
# 				{
# 					"field": "age",
# 					"descending": false
# 				}
# 			]
# 		},
# 		{
# 			"filter": [
# 				{
# 					"field": "race_description",
# 					"operator": "startswith",
# 					"value": "Black",
# 					"exclude": false
# 				}
# 			],
# 			"group": {
# 				"by": [
# 					"race_description",
# 					"ave"
# 				]
# 			}
# 		}
# 	],
# 	"limit": {
# 		"type": "first",
# 		"num": 3
# 	}
# }
