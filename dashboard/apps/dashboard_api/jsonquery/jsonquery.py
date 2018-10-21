from typing import Dict, List, Type
from django.db import models
from django.db.models import Model, QuerySet, Q, ForeignKey, F
from functools import reduce

# ========================================================================= #
# AGGREGATE METHODS                                                         #
# ========================================================================= #
from jsonschema import validate, ValidationError, SchemaError

from dashboard.apps.dashboard_api.management.util.modelinfo import ModelInfo

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
# Defines the scheme that a request must follow.                            #
# Advantage is the scheme can be validated on both the front and back end.  #
# ========================================================================= #

schema_filter = {
    "type": "array",
    "items": {  # list of different filters, each filter is effectively an & operation
        "type": "object",
        "properties": {
            "field": {"type": "string"},
            "operator": {"type": "string"},
            "value": {  # single string or list of different values for filters, each is effectively an | operation
                "anyOf": [{
                        "type": "array",
                        "minItems": 1,
                    }, {
                        "type": "string"
                    }
                ],
            },
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
schema_annotate = {
    "type": "array",
    "items": {  # list of different filters, each filter is effectively an & operation
        "type": "object",
        "properties": {
            "field": {"type": "string"},
            "operator": {"type": "string"},
            "value": {"type": "string"},
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
        "yield": {  # TODO, change to reuse annotate
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
                    "from",
                ],
            },
            "uniqueItems": True,
            "minItems": 0,
        },
        "distinctGrouping": {"type":"boolean"},
        "removeDuplicateCountings": {"type":"boolean"},
    },
    "required": [
        "by",
        "distinctGrouping",
        "removeDuplicateCountings",
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
        "type": {  # named 'type', not schema type
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
        "annotate": schema_annotate,
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
    for i, f in enumerate(fragment):
        # fragment[i]['field'] = _rename_field(queryset.model, f['field'])
        if 'exclude' not in f:
            f['exclude'] = False
        filterer = (queryset.exclude if f['exclude'] else queryset.filter)
        if type(f['value']) == str:
            f['value'] = [f['value']]
        q_values = [Q(**{f"{f['field']}__{f['operator']}": value}) for value in f['value']]
        queryset = filterer(reduce(lambda a, b: a | b, q_values))  # TODO: Add method of selecting option
    return queryset

def _annotate(queryset: QuerySet, fragment: List):
    for i, f in enumerate(fragment):
        queryset = queryset.annotate(**{f['field']: AGGREGATE_METHODS[f['operator']](f['value'])})
    return queryset


def _group(queryset: QuerySet, fragment: Dict):
    # group by student number to remove duplicates
    # (i.e. student takes 2 courses being grouped shouldnt be counted twice)

    # for j, name in enumerate(fragment['by']):
    #     fragment['by'][j] = _rename_field(queryset.model, name)

    # return early
    if 'yield' not in fragment:
        fragment['yield'] = []

    # find these unique pairs
    if len(fragment['yield']) == 0:
        if len(fragment['by']) == 1:
            unique = queryset.order_by(*fragment['by']).values_list(*fragment['by'], flat=True)
        else:
            unique = queryset.order_by(*fragment['by']).values_list(*fragment['by'])
    else:
        unique = queryset.order_by(*fragment['by']).values(*fragment['by'])

    if fragment['distinctGrouping'] == True:
        unique = unique.distinct()

    # data generators
    yields = {}
    for y in fragment['yield']:
        if 'via' in y:
            if y['from'] != '':
                (_via, _from) = (y['via'], y['from'])
                name = y['name'] if 'name' in y else f"{_from}_{_via}"
                if fragment['removeDuplicateCountings'] == True:
                    #https://stackoverflow.com/questions/52907276/django-queryset-aggregation-count-counting-wrong-thing#52907353
                    yields[name] = AGGREGATE_METHODS[_via](
                                        # _rename_field(queryset.model, 'encrypted_student_no'),\
                                        'encrypted_student_no',
                                        distinct=True)
                else:
                    # yields[name] = AGGREGATE_METHODS[_via](_rename_field(queryset.model, _from))
                    yields[name] = AGGREGATE_METHODS[_via](_from)
        else:
            yields[y['name'] if 'name' in y else y['from']] = F(y['from'])

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


def _rename_field(model, name):
    for field in model._meta.get_fields():
        if name == field.name:
            return name
        elif field.__class__ is ForeignKey:
            temp = _rename_field(field.remote_field.model, name)
            if temp != "":
                return field.name + "__" + temp
    return name


def parse_request(model: Type[Model], data: Dict):
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
            if 'annotate' in frag:
                queryset = _annotate(queryset, frag['annotate'])
            if 'group' in frag:
                queryset = _group(queryset, frag['group'])
            if 'order' in frag:
                queryset = _order(queryset, frag['order'])
    else:
        queryset = queryset.all()

    queryset = _limit(queryset, data['limit'] if 'limit' in data else {"type": "first", "num": -1})

    return queryset


def parse_options(model: Type[Model], data: Dict):
    try:
        validate(data, schema_query)
    except ValidationError as e:
        return False
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    try:
        # TODO, dynamically change based on query.
        return ModelInfo.static_generate_query_tree(model)
    except:
        print("FAILED IN parse_options")
        return {}


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
