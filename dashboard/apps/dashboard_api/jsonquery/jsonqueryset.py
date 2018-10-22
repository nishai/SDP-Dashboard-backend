import re
from pprint import pprint
from typing import Dict, List, Type
from asteval import asteval
from django.db import models
from django.db.models import Model, QuerySet
from jsonschema import validate, ValidationError, SchemaError

# ========================================================================= #
# AGGREGATE METHODS                                                         #
# ========================================================================= #

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

FILTER_METHODS = {
    "F": models.F,  # An object capable of resolving references to existing query objects or fields (ex. F(my_field) + 1).
    "Q": models.Q,  # Encapsulate filters as objects that can then be combined logically (using `&` and `|`).
}

ANNOTATE_METHODS = {
    "F": models.F,  # An object capable of resolving references to existing query objects or fields (ex. F(my_field) + 1).
}


# ========================================================================= #
# SCHEMA - https://json-schema.org & https://pypi.org/project/jsonschema    #
# Defines the scheme that a request must follow.                            #
# Advantage is the scheme can be validated on both the front and back end.  #
# ========================================================================= #

def schema_any(*types):
    return {"anyOf": list(types)}


def schema_enum(*values):
    return {"enum": list(values)}


def schema_object(properties, not_required=None, definitions=None):
    if not_required is None:
        not_required = set()
    if definitions is None:
        definitions = {}
    return {
        "type": "object",
        "properties": properties,
        "required": list(set(properties) - set(not_required)),
        "additionalProperties": False,
        "definitions": definitions
    }


def schema_array(items=None, unique=True, min_size=0):
    return {
        "type": "array",
        "items": items,
        "uniqueItems": unique,
        "minItems": min_size,
    }


def schema_action(type_name, data=None, not_required=None):
    assert (type(data) == dict and 'action' not in data) or (data is None)
    if data is None:
        return schema_object({
            'action': {"const": type_name}
        })
    else:
        return schema_object({
            'action': {"const": type_name},
            **data
        }, not_required=set([] if not_required is None else not_required) - {'action'})

# Methods that return new QuerySets: https://docs.djangoproject.com/en/2.1/ref/models/querysets/
#   o   filter()
#   o   exclude()
#   o   annotate()
#   o   order_by()
#   o   [:10] NOT [-5:]
#   o   reverse()
#   o   distinct()
#   o   all()
#   o   none()
#   -   &
#   -   |

schema_queryset = schema_object({
    "query": schema_array(schema_any(
        # data based actions
        schema_action('filter', {
            "expr": {"type": "string"}
        }),
        schema_action('exclude', {
            "expr": {"type": "string"}
        }),
        schema_action('annotate', {
            "fields": schema_array(
                schema_object({
                    "field": {"type": "string"},
                    "expr": {"type": "string"},
                })
            )
        }),
        schema_action('values', {
            "fields": schema_array(
                {"type": "string"}
            )
        }),
        schema_action('order_by', {
            "fields": schema_array(
                schema_object({
                    "field": {"type": "string"},
                    "descending": {"type": "boolean"},
                }, not_required=['descending'])
            )
        }),
        schema_action('limit', {
            "method": {"enum": ["first", "last", "page"]},
            "num": {"type": "integer"},
            "index": {"type": "integer"},
        }, not_required=['index']),
        # # # singular actions
        schema_action('reverse'),
        schema_action('distinct'),
        schema_action('all'),
        schema_action('none'),
    )),
})


# ========================================================================= #
# PARSERS                                                                   #
# ========================================================================= #

def _filter(queryset: QuerySet, fragment: str, exclude=False):
    expr = re.sub("[\n \t]", " ", fragment['expr'])
    if "Q(" not in expr:
        raise Exception("expression does not contain Q(...)")
    # interpreter
    _aeval = asteval.Interpreter(
        symtable={**AGGREGATE_METHODS, **FILTER_METHODS},
        use_numpy=False,
        minimal=True,
        builtins_readonly=True
    )
    # filter
    expr = _aeval(expr)
    if not isinstance(expr, models.Q):
        raise Exception("expression must produce an instance of models.Q")
    return (queryset.exclude if exclude else queryset.filter)(expr)


def _annotate(queryset: QuerySet, fragment: List):
    # interpreter
    _aeval = asteval.Interpreter(
        symtable={**AGGREGATE_METHODS, **ANNOTATE_METHODS},
        use_numpy=False,
        minimal=True,
        builtins_readonly=True
    )
    # annotate
    annotate = {}
    for f in fragment['fields']:
        (field, expr) = f['field'], f['expr']
        expr = re.sub("[\n \t]", " ", expr)
        expr = expr if not "'" in expr and not '"' in expr else _aeval(expr)
        annotate[field] = expr
    return queryset.annotate(**annotate)


def _order_by(queryset: QuerySet, fragment: List[Dict]):
    return queryset.order_by(*[
        (("-" + order['field']) if ('descending' in order and order['descending']) else order['field'])
        for order in fragment['fields']
    ])


def _limit(queryset: QuerySet, fragment: Dict[str, object]):
    (method, num) = fragment['method'], fragment['num']

    if num == -1:
        return queryset

    if method == 'page':
        i = fragment['index'] if 'index' in fragment else 0
        return queryset[max(0, i * num):min((i + 1) * num, len(queryset))]
    else:
        if method == 'last':
            queryset.reverse()
        return queryset[:min(num, len(queryset))]



def parse_request(model: Type[Model], data: Dict):
    try:
        validate(data, schema_queryset)
    except ValidationError as e:
        raise e
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    queryset = model.objects.all().values()

    if 'query' in data and len(data['query']) > 0:
        for i, fragment in enumerate(data['query']):
            ftype = fragment['action']
            if ftype == 'filter':
                queryset = _filter(queryset, fragment, exclude=False)
            elif ftype == 'exclude':
                queryset = _filter(queryset, fragment, exclude=True)
            elif ftype == 'annotate':
                queryset = _annotate(queryset, fragment)
            elif ftype == 'values':
                queryset = queryset.values(*fragment['fields'])
            elif ftype == 'order_by':
                queryset = _order_by(queryset, fragment)
            elif ftype == 'limit':
                queryset = _limit(queryset, fragment)
            elif ftype == "reverse":
                queryset = queryset.reverse()
            elif ftype == "distinct":
                queryset = queryset.distinct()
            elif ftype == "all":
                queryset = queryset.all()
            elif ftype == "none":
                queryset = queryset.none()

    return queryset


def parse_options(model: Type[Model], data: Dict):
    try:
        validate(data, schema_queryset)
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

