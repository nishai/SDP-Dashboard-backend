import copy
import datetime
from typing import Type

from asteval import asteval
from django.db import models
from django.db.models import QuerySet
from django.utils.datastructures import OrderedSet

from dashboard.apps.dashboard_api.jsonquery.schema import Schema

# ========================================================================= #
# EXPORT                                                                    #
# ========================================================================= #

ACTIONS = {}

SCHEMA = Schema.object({
    "query": Schema.array(Schema.any()),
})


def register_action(cls: Type['QuerysetAction']):
    """
    Decorator that can be applied to QuerysetAction(s) to
    register them with this modules ACTIONS & SCHEMA
    """
    instance = cls()
    ACTIONS[instance.name] = instance
    any_list = SCHEMA['properties']['query']['items']['anyOf']
    if instance.name in set(f['properties']['action']['const'] for f in any_list):
        raise RuntimeError(f"Duplicate name found: {instance.name}")
    any_list.append(instance.get_schema())
    return cls


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
    "date": datetime.date
}

_FILTER_METHODS = {
    "Q": models.Q,  # Encapsulate filters as objects that can then be combined logically (using `&` and `|`).
    **_ANNOTATE_METHODS,
}

_AEVAL_FILTER = asteval.Interpreter(
    symtable={**_AGGREGATE_METHODS, **_FILTER_METHODS},
    use_numpy=False, minimal=True, builtins_readonly=True
)

_AEVAL_ANNOTATE = asteval.Interpreter(
    symtable={**_AGGREGATE_METHODS, **_ANNOTATE_METHODS},
    use_numpy=False, minimal=True, builtins_readonly=True
)


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

    def fake(self, fakeset: dict, fragment: dict):
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
    """

    name = 'filter'
    properties = {
        "fields": Schema.any(  # TODO: rethink
            Schema.str,
            Schema.array(Schema.object({
                "field": Schema.str,
                "expr": Schema.str,
            }), min_size=1),
        )
    }
    _exclude = False

    def handle(self, queryset: QuerySet, fragment: dict):
        if type(fragment['fields']) == str:
            expr = _AEVAL_FILTER(fragment['fields'])
            if not isinstance(expr, models.Q):
                raise Exception("expression must produce an instance of models.Q")
        else:
            expr = None
            for f in fragment['fields']:
                q = models.Q(**{f['field']: _AEVAL_ANNOTATE(f['expr'])})
                expr = q if expr is None else (expr | q)
        return (queryset.exclude if self._exclude else queryset.filter)(expr)


@register_action
class ExcludeAction(FilterAction):
    """
    Action version of a QuerySet.exclude(...)
    The inverse of FilterAction
    """

    name = 'exclude'
    _exclude = True


@register_action
class AnnotateAction(QuerysetAction):
    """
    Action version of a QuerySet.annotate(...)
    - Use ValuesAction followed by AnnotateAction to "group_by"
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
            annotate[f['field']] = _AEVAL_ANNOTATE(f['expr'])
        return queryset.annotate(**annotate)

    def fake(self, fakeset: dict, fragment: dict):
        return {
            **fakeset,
            **{f['field']: None for f in fragment['fields']}
        }

@register_action
class ValuesAction(QuerysetAction):
    """
    Action version of a QuerySet.values(...)
    - Use ValuesAction followed by AnnotateAction to "group_by"
    """

    name = 'values'
    properties = {
        "fields": Schema.array(Schema.any(
            Schema.str,
            Schema.object({
                "field": Schema.str,
                "expr": Schema.str,
            })
        ))
    }
    not_required = ['fields']

    def _extract(self, fragment: dict):
        (fields, expressions, names) = [], {}, []
        for field in fragment['fields']:
            if type(field) == str:
                fields.append(field)
                names.append(field)
            elif type(field) == dict:
                expressions[field['field']] = _AEVAL_ANNOTATE(field['expr'])
                names.append(field['field'])
            else:
                assert False, "This should never happen"
        return (fields, expressions, names)

    def handle(self, queryset: QuerySet, fragment: dict):
        (fields, expressions, names) = self._extract(fragment)
        return queryset.values(*fields, **expressions)

    def fake(self, fakeset: dict, fragment: dict):
        (fields, expressions, names) = self._extract(fragment)
        return {
            **{f: None for f in names},
        }

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
        if 'fields' not in fragment:
            fragment['fields'] = []
        if 'flat' not in fragment:
            fragment['flat'] = False
        if 'named' not in fragment:
            fragment['named'] = False
        return queryset.values_list(*fragment['fields'], flat=fragment['flat'], named=fragment['named'])

    def fake(self, fakeset: dict, fragment: dict):
        return {f: None for f in fragment['fields']}


@register_action
class OrderByAction(QuerysetAction):
    """
    Action version of a QuerySet.order_by(...)
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
            return queryset[max(0, i * num):min((i + 1) * num, len(queryset))]
        else:
            if method == 'last':
                queryset.reverse()
            return queryset[:min(num, len(queryset))]


@register_action
class DistinctAction(QuerysetAction):
    """
    Action version of a QuerySet.distinct(...)
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
    """

    name = 'reverse'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.reverse()


@register_action
class AllAction(QuerysetAction):
    """
    Action version of a QuerySet.all()
    """

    name = 'all'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.all()


@register_action
class NoneAction(QuerysetAction):
    """
    Action version of a QuerySet.none(...)
    """

    name = 'none'

    def handle(self, queryset: QuerySet, fragment: dict):
        return queryset.none()
