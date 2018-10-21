import logging
from typing import Type
from django.db.models import Model, AutoField, ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from dashboard.apps.dashboard_api.management.util.errors import VisibleError

logger = logging.getLogger('debug-import')


class ModelInfo(object):
    """
    Helper object to find relationships between models.
    [Specific to the Inserter class]
    """

    def __init__(self, model: Type[Model]):
        self.model = model
        self.meta = self.model._meta
        self.name = self.meta.object_name  # self.meta.model_name

        # QUERIES
        # =======
        self.query_field_map = self._generate_query_tree(model)

        # HIERARCHY - TODO: find unnecessary data and remove, or create data structure for fields too.
        # =========
        self.field_map = {f.name: f for f in self.meta.get_fields() if not isinstance(f, ForeignObjectRel) and not isinstance(f, AutoField) and f.name != 'id'}
        self.foreign_field_map = {n: f for n, f in self.field_map.items() if isinstance(f, ForeignKey)}
        self.foreign_models_map = {n: ModelInfo(f.related_model) for n, f in self.foreign_field_map.items()}
        # unique
        if len(self.meta.unique_together) > 0:
            self.unique_map = {n: self.field_map[n] for n in self.meta.unique_together[0]}
        else:
            logger.warning(f"[{self.model.__name__}]: No Uniqueness Constraints Specified, defaulting to primary key '{self.meta.pk.name}'")
            if not isinstance(self.meta.pk, AutoField) and self.meta.pk.name != 'id':
                self.unique_map = {self.meta.pk.name: self.meta.pk}
            else:
                raise VisibleError(f"Defaulting to primary key '{self.meta.pk.name}' failed, try specifying a uniqueness constraint on '{self.name}'")
        # uniqueness map
        self.unique_flat_map = {itemn: itemf for n, f in self.unique_map.items() for itemn, itemf in (self.foreign_models_map[n].unique_flat_map.items() if (n in self.foreign_models_map) else {n: f}.items())}
        # foreign
        self.foreign_unique_map = {n: self.foreign_models_map[n].unique_flat_map for n in self.foreign_field_map}
        self.foreign_flat = {n: f for uk, uv in self.foreign_unique_map.items() for n, f in uv.items()}
        # all fields needed to generate a record for this model, including finding dependencies by their unique values and record data
        self.dependent = set(self.foreign_flat) | (set(self.field_map) - set(self.foreign_field_map))
        self.dependent_non_null = {n for n in self.dependent if n in self.foreign_flat or (n in self.field_map and not self.field_map[n].null)}

    def print_hierarchy(self, index_stack=None):
        """
        Print the hierarchy of the current model based on foreign keys,
        listing the foreign keys for each model in the tree,
        and their associated composite key that represents them.
        """

        if index_stack is None:
            index_stack = []
        # generate path
        s = ''
        for i, l in index_stack:
            s += '│   ' if i+1 < l else '    '
        # print strings
        print(f"{s}[\033[91m{self.name}\033[00m]")
        for index, (n, m) in enumerate(self.foreign_models_map.items()):
            print(f"{s}{'├─' if index+1 < len(self.foreign_models_map) else '└─'}\033[93m{n}\033[00m" + ('' if len(self.foreign_unique_map[n]) <= 1 else f" -> ({', '.join(sorted(self.foreign_unique_map[n]))})"))
            m.print_hierarchy(index_stack=index_stack + [(index, len(self.foreign_models_map))])

    def _generate_query_tree(self):
        return self.static_generate_query_tree(self.model)

    @staticmethod
    def static_generate_query_tree(self, model: Type[Model], field_stack=None, dictionary=None):
        """
        Generate a dictionary of all the fields accessible from this model,
        including via foreign keys.
        """
        if dictionary is None:
            dictionary = dict()
        if field_stack is None:
            field_stack = []
        for field in model._meta.get_fields():
            path = '__'.join(field_stack + [field.name])
            if path in dictionary:
                raise RuntimeError("Path already in dictionary, is something wrong with your model?")
            dictionary[path] = field
            if isinstance(field, ForeignKey):
                ModelInfo.static_generate_query_tree(field.related_model, field_stack=field_stack + [field.name], dictionary=dictionary)
        return dictionary

    def print_query_tree(self):
        self.static_print_query_tree(self.model)

    @staticmethod
    def static_print_query_tree(model: Type[Model], index_stack=None):
        """
        Print the hierarchy of the current model based on foreign keys,
        listing the full query name for each field under the model.
        """
        if index_stack is None:
            index_stack = []
        # generate path
        s = ''
        for i, l, n in index_stack:
            s += '│   ' if i+1 < l else '    '
        # print strings
        print(f"{s}[\033[91m{model._meta.object_name}\033[00m]")
        for index, field in enumerate(model._meta.get_fields()):
            path = '__'.join([n for i, l, n in index_stack] + [f'\033[93m{field.name}\033[00m'])
            print(f"{s}{'├─' if index+1 < len(model._meta.get_fields()) else '└─'}\033[90m{path}\033[00m")
            if isinstance(field, ForeignKey):
                ModelInfo.static_print_query_tree(field.related_model, index_stack=index_stack + [(index, len(model._meta.get_fields()), field.name)])

