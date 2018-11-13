import copy
import datetime
import operator
from typing import Type
from asteval import asteval
from django.db import models
from django.db.models import QuerySet, Model, When, Case, Value
from datetime import timedelta
from django.utils import timezone
from dashboard.apps.wits.parser.schema import Schema
from jsonschema import validate, ValidationError, SchemaError
from dashboard.shared.model import get_model_relations


# ========================================================================= #
# EXPORT                                                                    #
# ========================================================================= #

"""
All action classes registered by (the annotation) register_action.
All parse methods can have these classes applied.
RETURN QUERYSETS
"""
ACTIONS = {}

"""
All action classes registered by (the annotation) register_action.
All parse methods can have these classes applied.
FINAL ACTION ON A QUERYSET
"""
FINALS = {}

"""
Base object representing the schema for all requests.
See JSON Schema for details.
"""
SCHEMA = Schema.object({
    "queryset": Schema.array(Schema.any()),
    "explain": Schema.bool,
    # "fake": Schema.bool, # TODO, remove parameter from query
}, not_required='explain')

def register(cls: Type['QuerysetAction'], dict_obj: dict):
    instance = cls()
    if instance.name in dict_obj:
        raise RuntimeError(f"Duplicate name found: {instance.name}")
    dict_obj[instance.name] = instance
    any_list = SCHEMA['properties']['queryset']['items']['anyOf']
    if instance.name in set(f['properties']['action']['const'] for f in any_list):
        raise RuntimeError(f"Duplicate name found: {instance.name}")
    any_list.append(instance.get_schema())
    return cls



def register_action(cls: Type['QuerysetAction']):
    """
    Decorator that can be applied to QuerysetAction(s) to
    register them with this modules ACTIONS & SCHEMA
    """
    return register(cls, ACTIONS)


def register_final(cls: Type['QuerysetAction']):
    """
    Decorator that can be applied to QuerysetAction(s) to
    register them with this modules FINALS & SCHEMA
    - these end the queryset, by returning data.
    """
    return register(cls, FINALS)


# ========================================================================= #
# REQUEST HANDLERS                                                          #
# TODO: check https://github.com/carltongibson/django-filter                #
# ========================================================================= #


def parse_request(model: Type[Model], data: dict, fake=False):
    """
    Intended to parse a data dictionary with valid schema,
    and generate the corresponding queryset from the model.

    Queryset Example:
    =================
      ExampleModel.objects.all()
      .values('course_code', 'enrolled_year_id__progress_outcome_type')
      .annotate(asdf=Maximum('final_mark'), year=F('enrolled_year_id__calendar_instance_year'))
      .order_by('asdf')

    Is the same as:
    ===============
    # TODO: this might be wrong
    {
        "explain": true,
        "queryset": [
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
                "action": "order_by",
                "fields": [
                    {
                        "field": "asdf",
                        "descending": true
                    }
                ]
            },
            {
                "action": "values"
            },
            {
                "action": "limit",
                "method": "first",
                "num": 100
            }
        ]
    }

    :param model: The django model to generate the queryset for.
    :param data: A dictionary representing the query
    :param fake: Indicates if, instead, only a (approximate) list of the field names of the queryset should be returned.
    :return: A queryset (if fake=False) or list (if fake=True) PLUS the explanation if requested PLUS a boolean variable is_final
    """
    try:
        validate(data, SCHEMA)
    except ValidationError as e:
        raise e
    except SchemaError as e:
        raise e  # we caused this with invalid schema above

    queryset = [f.attname for f in model._meta.concrete_fields] if fake else model.objects.all().values()
    explanation, should_explain = None, 'explain' in data and data['explain']

    is_final = False
    if 'queryset' in data and len(data['queryset']) > 0:
        for i, fragment in enumerate(data['queryset']):
            # check that a final action hasnt already been called.
            if is_final:
                raise Exception('Final actions must be at the end of the queryset.')
            # get actions
            if fragment['action'] in ACTIONS:
                (action, is_final) = (ACTIONS[fragment['action']], False)
            elif fragment['action'] in FINALS:
                (action, is_final) = (FINALS[fragment['action']], True)
            else:
                raise Exception('Invalid action: ' + fragment['action'])  # this should never happen.

            if is_final and should_explain:
                explanation = queryset.explain()

            # get the data from the action
            queryset = action.fake(model, queryset, fragment) if fake else action.handle(queryset, fragment)

    if not is_final and should_explain:
        explanation = queryset.explain()

    return queryset, explanation, is_final


def parse_options(model: Type[Model], data: dict):
    """
    Returns a list of all fields accesible from the current model,
    including from parents and foreign keys,
    as well as including keys generated by the query itself - from parse_request with fake=True.

    :param model: The django model to generate the list for.
    :param data: A dictionary representing the query
    :return: A set of field names
    """
    return set(get_model_relations(model, reverse_relations=True, foreign_relations=True)) | set(parse_request(model, data, fake=True))


# ========================================================================= #
# CONSTS                                                                    #
# ========================================================================= #


_AGGREGATE_METHODS = {
    "max": models.Max,
    "min": models.Min,
    "std": models.StdDev,
    "sum": models.Sum,
    "var": models.Variance,
    "ave": models.Avg,
    "count": models.Count,
}

_ANNOTATE_METHODS = {
    "F": models.F,  # An object capable of resolving references to existing query objects or fields (ex. F(my_field) + 1).
    # sql generators - https://docs.djangoproject.com/en/2.0/ref/models/conditional-expressions/#conditional-aggregation
    "When": When,
    "Case": Case,
    "Value": Value,
    # util packages
    "date": datetime.date,
    "timedelta": timedelta,
    "timezone": timezone,
}

_FILTER_METHODS = {
    "Q": models.Q,  # Encapsulate filters as objects that can then be combined logically (using `&` and `|`).
    **_ANNOTATE_METHODS,
}

_AEVAL_FILTER_INTERPRETER = asteval.Interpreter(
    symtable={**_AGGREGATE_METHODS, **_FILTER_METHODS},
    use_numpy=False, minimal=True, builtins_readonly=True
)

_AEVAL_FILTER = lambda expr: _AEVAL_FILTER_INTERPRETER.eval(expr, show_errors=False)  # throw exceptions instead

_AEVAL_ANNOTATE_INTERPRETER = asteval.Interpreter(
    symtable={**_AGGREGATE_METHODS, **_ANNOTATE_METHODS},
    use_numpy=False, minimal=True, builtins_readonly=True
)

_AEVAL_ANNOTATE = lambda expr: _AEVAL_ANNOTATE_INTERPRETER.eval(expr, show_errors=False)  # throw exceptions instead


# ========================================================================= #
# BASE ACTION                                                               #
# ========================================================================= #


class QuerysetAction(object):
    """
    Base object for all Actions.
    Actions are performed on a queryset
    Has the capability to simulate an action for documentation purposes
    """

    name = None
    properties = None
    not_required = set()

    def get_schema(self):
        """
        Returns a new jsonschema object defining what
        the actions fragment should look like,
        based on the properties, name and not_required
        """
        if type(self.properties) != dict and self.properties is not None:
            raise NotImplementedError("'properties' must be None or a Dict")
        if type(self.name) != str:
            raise NotImplementedError("'name' must be a string")
        if type(self.not_required) not in [list, set]:
            raise NotImplementedError("'not_required' must be set-like")
        return copy.deepcopy(Schema.action(self.name, data=self.properties, not_required=self.not_required))

    def handle(self, queryset: QuerySet, fragment: dict):
        """
        Handles a fragment from a query,
        to return a mutated queryset
        """
        raise NotImplementedError()

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        """
        Fake operations on a queryset,
        by just mutating the fields in a dictionary
        """
        return fakeset


# ========================================================================= #
# ACTIONS                                                                   #
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

@register_action
class FilterAction(QuerysetAction):
    """
    Action version of a QuerySet.filter(...)

    Example Expression 01:
    {
        "action": "filter",
        "expr": "Q(question__startswith='Who', pub_date__year=2004) | ~Q(pub_date__year=2005)"
    }

    Example Expression 02 (Equivalent):
    {
        "action": "filter",
        "expr": "Q(question__startswith='Who') & Q(pub_date__year=F('del_date__year') + 4 - 1) | ~Q(pub_date__year=2005)"
    }

    Example RPN Expression:
    {
        "action": "filter",
        "expr": [
            {
                "meta": "question__startswith",
                "expr": "Who"
            },
            {
                "meta": "pub_date__exact",
                "expr": "2014"
            },
            "&",
            {
                "meta": "pub_date__exact",
                "expr": "2005"
            },
            "~",
            "|"
        ]
    }
    """

    name = 'filter'
    properties = {
        "expr": Schema.any(
            Schema.str,                     # 1. single expression formed from Q() statements.
            Schema.array(Schema.any(        # 2. generate single expression using RPN methods (https://en.wikipedia.org/wiki/Reverse_Polish_notation)
                Schema.enum('|', '&', '~'),     # RPN operator ('|')
                Schema.object({                 # RPN element representing a single Q() statement with one parameter
                    "meta": Schema.str,             # pub_date__year__exact eg. Q(pub_date__year=F('del_date__year')+4)
                    "expr": Schema.any(
                        Schema.str,
                        Schema.array(
                            Schema.any(Schema.str, Schema.int, Schema.bool, Schema.float, Schema.null),
                            min_size=0,
                        )
                    ),             # F('del_date__year')+4 eg. Q(pub_date__year=F('del_date__year')+4) # TODO convert into similar RPN Stack
                }),
            ), min_size=1),
        )
    }
    _exclude = False

    def handle(self, queryset: QuerySet, fragment: dict):
        if type(fragment['expr']) == str:   # 1. (above)
            # Evaluate Single Expression String

            try:
                expr = _AEVAL_FILTER(fragment['expr'])
            except Exception as e:
                raise RuntimeError('Invalid Expression: ' + fragment['expr']).with_traceback(e.__traceback__)

            if not isinstance(expr, models.Q):
                raise Exception("expression must produce an instance of models.Q")
            # return filtered expression
            try:
                return (queryset.exclude if self._exclude else queryset.filter)(expr)
            except ValueError as e:
                raise ValueError("Probably a malformed query expression, check your Q()").with_traceback(e.__traceback__)
        else:                               # 2. (above)
            # RPN Stack Calculator
            (stack, ops1, ops2) = [], {'~': operator.inv}, {'&': operator.and_, '|': operator.or_}
            for token in fragment['expr']:
                if type(token) == str:
                    if token in ops1:
                        if len(stack) < 1:
                            raise ValueError('Must have at least one parameter to perform op')
                        a = stack.pop()
                        if not isinstance(a, models.Q):
                            raise ValueError('Negation cannot be applied to operator.')
                        stack.append(ops1[token](a))
                    else:
                        if len(stack) < 2:
                            raise ValueError('Must have at least two parameters to perform op')
                        a = stack.pop()
                        b = stack.pop()
                        stack.append(ops2[token](b, a))
                    # NO THIRD CASE DUE TO JSON SCHEMA
                else:
                    if type(token) == list:
                        if not token['meta'].endswith("__in"):
                            raise Exception("expr of type array, must use operator 'in'")
                        result = token['expr']
                    else:
                        try:
                            result = _AEVAL_ANNOTATE(token['expr'])
                        except Exception as e:
                            result = token['expr']
                            # raise RuntimeError('Invalid Expression: ' + token['expr']).with_traceback(e.__traceback__)
                    stack.append(models.Q(**{token['meta']: result}))
                # NO THIRD CASE DUE TO JSON SCHEMA
            expr = stack.pop()
            if len(stack) > 0:
                raise ValueError("No more operators, not all values consumed.")
            # return filtered expression
            return (queryset.exclude if self._exclude else queryset.filter)(expr)


@register_action
class ExcludeAction(FilterAction):
    """
    Action version of a QuerySet.exclude(...)
    The inverse of FilterAction

    Example:
        See FilterAction
    """

    name = 'exclude'
    _exclude = True


@register_action
class AnnotateAction(QuerysetAction):
    """
    Action version of a QuerySet.annotate(...)
    - Use ValuesAction followed by AnnotateAction to "group_by"

    Example:
    {
        "action": "annotate",
        "fields": [
            {
                "field": "asdf",
                "expr": "max('final_mark')"
            },
            {
                "field": "year",
                "expr": "-2000 + F('enrolled_year_id__calendar_instance_year')"     # TODO: add support for string entries
            }
        ]
    }
    """

    name = 'annotate'
    properties = {
        "fields": Schema.array(
            Schema.object({
                "field": Schema.str,
                "expr": Schema.str,
            })
        )
    }

    def handle(self, queryset: QuerySet, fragment: dict):
        annotate = {}
        for f in fragment['fields']:
            try:
                annotate[f['field']] = _AEVAL_ANNOTATE(f['expr'])
            except Exception as e:
                raise RuntimeError('Invalid Expression: ' + f['expr']).with_traceback(e.__traceback__)
        return queryset.annotate(**annotate)

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        return fakeset + [f['field'] for f in fragment['fields'] if f['field'] not in fakeset]

@register_action
class ValuesAction(QuerysetAction):
    """
    Action version of a QuerySet.values(...)
    - Use ValuesAction followed by AnnotateAction to "group_by"

    Example:
    {
        "action": "values",
        "fields": [
            "course_code",
            "enrolled_year_id__progress_outcome_type"
        ]
    }
    """

    name = 'values'
    properties = {
        "fields": Schema.array(Schema.any(
            Schema.str,
            Schema.object({
                "field": Schema.str,
                "expr": Schema.str,
            })
        ), min_size=1)
    }

    def _extract(self, fragment: dict):
        if len(fragment['fields']) < 1:
            raise Exception("'fields' must contain values - this limitation will hopefully be removed in future")
        (fields, expressions, names) = [], {}, []  # names exists so the fields dont go out of order.
        for field in fragment['fields']:
            if type(field) == str:
                fields.append(field)
                names.append(field)
            elif type(field) == dict:
                try:
                    expressions[field['field']] = _AEVAL_ANNOTATE(field['expr'])
                except Exception as e:
                    raise RuntimeError('Invalid Expression: ' + field['expr']).with_traceback(e.__traceback__)
                names.append(field['field'])
            else:
                assert False, "This should never happen"
        return (fields, expressions, names)

    def handle(self, queryset: QuerySet, fragment: dict):
        (fields, expressions, names) = self._extract(fragment)
        queryset = queryset.values(*fields, **expressions)
        return queryset

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        (fields, expressions, names) = self._extract(fragment)
        if len(names) > 0:
            return names
        else:
            # TODO: this needs to emulate the queryset, and store separate values for annotations, values, expressions etc.
            # logic taken from queryset.query.set_values
            concrete_fields = [f.attname for f in model._meta.concrete_fields]
            return concrete_fields + [f for f in fakeset if f not in concrete_fields]

@register_action
class ValuesListAction(QuerysetAction):
    """
    Action version of a QuerySet.values_list(...)
    Indicates that a QuerySet should rather be serialised as
    an array of tuples instead of an array of dictionaries
    """

    name = 'values_list'
    properties = {
        "fields": Schema.array(Schema.str),
        "flat": Schema.bool,
        "named": Schema.bool,
    }
    not_required = ['fields', 'flat', 'named']

    def handle(self, queryset: QuerySet, fragment: dict):
        # TODO: does this behave the same as values() when no fields are passed?
        if 'fields' not in fragment:
            fragment['fields'] = []
        if 'flat' not in fragment:
            fragment['flat'] = False
        if 'named' not in fragment:
            fragment['named'] = False
        return queryset.values_list(*fragment['fields'], flat=fragment['flat'], named=fragment['named'])

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        return [f for f in fragment['fields']]


@register_action
class OrderByAction(QuerysetAction):
    """
    Action version of a QuerySet.order_by(...)

    Example:
    {
        "action": "order_by",
        "fields": [
            {
                "field": "asdf",
                "descending": true
            }
        ]
    },

    NOTE: order_by does not necessarily need to be placed at the end of a queryset.
    For example slices do not support ordering, and so this needs to be called before hand, even though values may not yet exist for this.

    {
        "queryset": [
            {
                "action": "order_by",                                                                   <<< take note
                "fields": [
                    {
                        "field": "asdf",                                                                <<< take note
                        "descending": true
                    }
                ]
            },
            {
                "action": "limit",                                                                      <<< take note
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
                "action": "annotate",                                                                   <<< take note
                "fields": [
                    {
                        "field": "asdf",                                                                <<< take note
                        "expr": "max('final_mark')"
                    },
                    {
                        "field": "year",
                        "expr": "F('enrolled_year_id__calendar_instance_year')"
                    }
                ]
            }
        ]
    }
    """

    name = 'order_by'
    properties = {
        "fields": Schema.array(
            Schema.object({
                "field": Schema.str,
                "descending": Schema.bool,
            }, not_required=['descending'])
        )
    }

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.order_by(*[
            (("-" + order['field']) if ('descending' in order and order['descending']) else order['field'])
            for order in fragment['fields']
        ])


@register_action
class LimitAction(QuerysetAction):
    """
    Action version of a QuerySet[...]

    Example First:
    {
        "action": "limit",
        "method": "first",
        "num": 100
    }

    Example Last:
    {
        "action": "limit",
        "method": "last",
        "num": 100
    }

    Example Pages:
    {
        "action": "limit",
        "method": "page",
        "num": 10,
        "index": 3
    }
    """

    name = 'limit'
    properties = {
        "method": Schema.enum("first", "last", "page"),
        "num": Schema.int,
        "index": Schema.int,
    }
    not_required = ['index']

    def handle(self, queryset: QuerySet, fragment: dict):
        (method, num) = fragment['method'], fragment['num']
        if num == -1:
            return queryset
        if method == 'page':
            i = fragment['index'] if 'index' in fragment else 0
            offset = i * num
            return queryset[max(0, offset):min(offset + num, queryset.count())]
        else:
            if method == 'last':
                queryset.reverse()
            return queryset[0:min(num, queryset.count())]


@register_action
class DistinctAction(QuerysetAction):
    """
    Action version of a QuerySet.distinct(...)

    Example:
    {
        "action": "distinct"
    }
    """

    name = 'distinct'
    properties = {
        "fields": Schema.array(Schema.str)
    }

    def handle(self, queryset: QuerySet, fragment: dict):
        if 'fields' not in fragment:
            fragment['fields'] = []
        return queryset.distinct(*fragment['fields'])


@register_action
class ReverseAction(QuerysetAction):
    """
    Action version of a QuerySet.reverse()

    Example:
    {
        "action": "reverse"
    }
    """

    name = 'reverse'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.reverse()


@register_action
class AllAction(QuerysetAction):
    """
    Action version of a QuerySet.all()

    {
        "action": "all"
    }
    """

    name = 'all'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.all()


@register_action
class NoneAction(QuerysetAction):
    """
    Action version of a QuerySet.none(...)

    Example:
    {
        "action": "none"
    }
    """

    name = 'none'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.none()

# ========================================================================= #
# LOCKING ACTIONS - NOTHING CAN BE DONE AFTER - DO NOT RETURN QUERYSETS     #
# ========================================================================= #

@register_final
class CountAction(QuerysetAction):
    """
    Action version of a QuerySet.none(...)

    Example:
    {
        "action": "count"
    }
    """

    name = 'count'

    def handle(self, queryset: QuerySet, fragment: dict):
        return {'count': queryset.count()}

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        raise Exception("Actions that do not return a queryset are not supported.")

@register_final
class FirstAction(QuerysetAction):
    """
    Action version of a QuerySet.none(...)

    Example:
    {
        "action": "first"
    }
    """

    name = 'first'

    def handle(self, queryset: QuerySet, fragment: dict):
        return {'first': queryset.first()}

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        raise Exception("Actions that do not return a queryset are not supported.")

@register_final
class LastAction(QuerysetAction):
    """
    Action version of a QuerySet.none(...)

    Example:
    {
        "action": "last"
    }
    """

    name = 'last'

    def handle(self, queryset: QuerySet, fragment: dict):
        return {'last': queryset.last()}

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        raise Exception("Actions that do not return a queryset are not supported.")


@register_final
class AggregateAction(QuerysetAction):
    """
    Effectively the same as annotate, but operates on all the CURRENT elements,
    instead of the groupings.

    This should have the same api as annotate except
    that the list has to have at least one item.
    """

    name = 'aggregate'
    properties = {
        "fields": Schema.array(
            Schema.object({
                "field": Schema.str,
                "expr": Schema.str,
            }), min_size=1
        )
    }

    def handle(self, queryset: QuerySet, fragment: dict):
        aggregate = {}
        for f in fragment['fields']:
            try:
                aggregate[f['field']] = _AEVAL_ANNOTATE(f['expr'])
            except Exception as e:
                raise RuntimeError('Invalid Expression: ' + f['expr']).with_traceback(e.__traceback__)
        return queryset.aggregate(**aggregate)

    def fake(self, model: Type[Model], fakeset: list, fragment: dict):
        raise Exception("Actions that do not return a queryset are not supported.")


# rather implemented as a parameter to the request.

# @register_final
# class ExplainAction(QuerysetAction):
#     """
#     Action version of a QuerySet.none(...)
#
#     Example:
#     {
#         "action": "explain"
#     }
#     """
#
#     name = 'explain'
#
#     def handle(self, queryset: QuerySet, fragment: dict):
#         return {'explanation': queryset.explain()}
#
#     def fake(self, model: Type[Model], fakeset: list, fragment: dict):
#         raise Exception("Actions that do not return a queryset are not supported.")

# ========================================================================= #
# NON-STANDARD ACTIONS                                                      #
# ========================================================================= #

# @register_action
# class GroupByAction(QuerysetAction):
#     name = "group_by"
#     properties = {
#         "values": ValuesAction.properties['fields'],
#         "yield": AnnotateAction.properties['fields']
#     }
#     not_required = ['yield']
#
#     def handle(self, queryset: QuerySet, fragment: dict):
#         queryset = ACTIONS['values'].handle(queryset, {"fields": fragment['values']})
#         queryset = ACTIONS['annotate'].handle(queryset, {"fields": fragment['yield'] if 'yield' in fragment else []})
#         return queryset
#
#     def fake(self, fakeset: dict, fragment: dict):
#         fakeset = ACTIONS['values'].fake(fakeset, {"fields": fragment['values']})
#         fakeset = ACTIONS['annotate'].fake(fakeset, {"fields": fragment['yield'] if 'yield' in fragment else []})
#         return fakeset
