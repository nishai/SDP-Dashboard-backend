import datetime
from typing import Dict, List, Type
from asteval import asteval
from django.db import models
from django.db.models import Model, QuerySet
from jsonschema import validate, ValidationError, SchemaError
from dashboard.apps.dashboard_api.management.util.modelinfo import ModelInfo

# ========================================================================= #
# AGGREGATE METHODS                                                         #
# ========================================================================= #

AGGREGATE_METHODS = {
    "max": models.Max,
    "min": models.Min,
    "std": models.StdDev,
    "sum": models.Sum,
    "var": models.Variance,
    "ave": models.Avg,
    "count": models.Count,
}

ANNOTATE_METHODS = {
    "F": models.F,  # An object capable of resolving references to existing query objects or fields (ex. F(my_field) + 1).
    "date": datetime.date
}

FILTER_METHODS = {
    "Q": models.Q,  # Encapsulate filters as objects that can then be combined logically (using `&` and `|`).
    **ANNOTATE_METHODS,
}


# ========================================================================= #
# SCHEMA - https://json-schema.org & https://pypi.org/project/jsonschema    #
# Defines the scheme that a request must follow.                            #
# Advantage is the scheme can be validated on both the front and back end.  #
# ========================================================================= #

class Schema:

    class classproperty(property):
        def __get__(self, cls, owner):
            return classmethod(self.fget).__get__(None, owner)()

    @classproperty
    def str(cls): return {"type": "string"}

    @classproperty
    def int(cls): return {"type": "integer"}

    @classproperty
    def bool(cls): return {"type": "boolean"}

    @classproperty
    def float(cls): return {"type": "number"}

    @classmethod
    def const(cls, value): return {"const": value}

    @classmethod
    def any(cls, *types): return {"anyOf": list(types)}

    @classmethod
    def enum(cls, *values): return {"enum": list(values)}

    @classmethod
    def object(cls, properties, not_required=None, definitions=None):
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

    @classmethod
    def array(cls, items=None, unique=True, min_size=0):
        return {
            "type": "array",
            "items": items,
            "uniqueItems": unique,
            "minItems": min_size
        }

    @classmethod
    def action(cls, type_name, data=None, not_required=None):
        assert (type(data) == dict and 'action' not in data) or (data is None)
        if data is None:
            return Schema.object({
                'action': {"const": type_name}
            })
        else:
            return Schema.object({
                'action': {"const": type_name},
                **data
            }, not_required=set([] if not_required is None else not_required) - {'action'})


# ========================================================================= #
# QUERY - SCHEMA                                                            #
# ========================================================================= #


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

schema_queryset = Schema.object({
    "query": Schema.array(Schema.any(
        # data based actions
        Schema.action('filter', {
            "fields": Schema.any(
                Schema.str,
                Schema.array(Schema.object({
                    "field": Schema.str,
                    "expr": Schema.str,
                }), min_size=1),
            )
        }),
        Schema.action('exclude', {
            "fields": Schema.any(
                Schema.str,
                Schema.array(Schema.object({
                    "field": Schema.str,
                    "expr": Schema.str,
                }), min_size=1),
            )
        }),
        Schema.action('annotate', {
            "fields": Schema.array(
                Schema.object({
                    "field": Schema.str,
                    "expr": Schema.str,
                })
            )
        }),
        Schema.action('values', {
            "fields": Schema.array(Schema.any(
                Schema.str,
                Schema.object({
                    "field": Schema.str,
                    "expr": Schema.str,
                })
            ))
        }, not_required=['fields']),
        Schema.action('values_list', {
            "fields": Schema.array(Schema.str),
            "flat": Schema.bool,
            "named": Schema.bool,
        }, not_required=['fields', 'flat', 'named']),
        Schema.action('order_by', {
            "fields": Schema.array(
                Schema.object({
                    "field": Schema.str,
                    "descending": Schema.bool,
                }, not_required=['descending'])
            )
        }),
        Schema.action('limit', {
            "method": Schema.enum("first", "last", "page"),
            "num": Schema.int,
            "index": Schema.int,
        }, not_required=['index']),
        # singular actions
        Schema.action('reverse'),
        Schema.action('distinct'),
        Schema.action('all'),
        Schema.action('none'),
    )),
})


# ========================================================================= #
# PARSERS                                                                   #
# ========================================================================= #

def _filter(queryset: QuerySet, fragment: str, exclude=False):
    if type(fragment['fields']) == str:
        # interpreter
        _aeval = asteval.Interpreter(
            symtable={**AGGREGATE_METHODS, **FILTER_METHODS},
            use_numpy=False, minimal=True, builtins_readonly=True
        )
        # filter
        expr = _aeval(fragment['fields'])
        if not isinstance(expr, models.Q):
            raise Exception("expression must produce an instance of models.Q")
    else:
        # interpreter
        _aeval = asteval.Interpreter(
            symtable={**AGGREGATE_METHODS, **ANNOTATE_METHODS},
            use_numpy=False, minimal=True, builtins_readonly=True
        )
        # filter
        expr = None
        for f in fragment['fields']:
            q = models.Q(**{f['field']: _aeval(f['expr'])})
            expr = q if expr is None else (expr | q)

    return (queryset.exclude if exclude else queryset.filter)(expr)


def _exclude(queryset: QuerySet, fragment: str):
    return _filter(queryset, fragment, exclude=True)


def _annotate(queryset: QuerySet, fragment: List):
    # interpreter
    _aeval = asteval.Interpreter(
        symtable={**AGGREGATE_METHODS, **ANNOTATE_METHODS},
        use_numpy=False, minimal=True, builtins_readonly=True
    )
    # annotate
    annotate = {}
    for f in fragment['fields']:
        annotate[f['field']] = _aeval(f['expr'])
    return queryset.annotate(**annotate)


def _values(queryset: QuerySet, fragment: List):
    # interpreter
    _aeval = asteval.Interpreter(
        symtable={**AGGREGATE_METHODS, **ANNOTATE_METHODS},
        use_numpy=False, minimal=True, builtins_readonly=True
    )
    # annotate
    (fields, expressions) = [], {}
    for field in fragment['fields']:
        if type(field) == str:
            fields.append(field)
        elif type(field) == dict:
            expressions[field['field']] = _aeval(field['expr'])
        else:
            assert False, "This should never happen"
    # return
    return queryset.values(*fields, **expressions)


def _values_list(queryset: QuerySet, fragment: List):
    if 'fields' not in fragment:
        fragment['fields'] = []
    if 'flat' not in fragment:
        fragment['flat'] = False
    if 'named' not in fragment:
        fragment['named'] = False
    return queryset.values_list(*fragment['fields'], flat=fragment['flat'], named=fragment['named'])


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


_action_map = {
    "filter": _filter,
    "exclude": _exclude,
    "annotate": _annotate,
    "values": _values,
    "values_list": _values_list,
    "order_by": _order_by,
    "limit": _limit,
    "reverse": lambda queryset, fragment: queryset.reverse(),
    "distinct": lambda queryset, fragment: queryset.distinct(),
    "all": lambda queryset, fragment: queryset.all(),
    "none": lambda queryset, fragment: queryset.none(),
}


# ========================================================================= #
# REQUEST HANDLERS                                                          #
# ========================================================================= #

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
            action = _action_map[fragment['action']]
            queryset = action(queryset, fragment)

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

