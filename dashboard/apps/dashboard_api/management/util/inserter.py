import logging
from pprint import pprint
from typing import Type
import pandas as pd
import numpy as np
from django.db import connection, transaction
from django.db.models import Model, ForeignKey, Field
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import model_to_dict
from dashboard.apps.dashboard_api.management.util.measure import Measure

logger = logging.getLogger('debug-import')

class VisibleError(RuntimeError):
    def __init__(self, desc):
        super(VisibleError, self).__init__(f"\n{'=' * 80}\n{desc}\n{'=' * 80}")


class ModelInfo():
    def __init__(self, model: Type[Model]):
        # model
        self.model = model
        self.meta = self.model._meta
        self.name = self.meta.object_name  # self.meta.model_name
        # maps
        self.field_map = {f.name: f for f in self.meta.get_fields() if not isinstance(f, ForeignObjectRel) and f.name != 'id'}
        # hierarchy
        self.foreign_reverse_relations_map = {n: f for n, f in self.field_map.items() if isinstance(f, ForeignObjectRel)}
        self.foreign_field_map = {n: f for n, f in self.field_map.items() if isinstance(f, ForeignKey)}
        self.foreign_models_map = {n: ModelInfo(f.related_model) for n, f in self.foreign_field_map.items()}
        # unique
        self.unique_map = {n: self.field_map[n] for n in self.meta.unique_together[0]} if (len(self.meta.unique_together) > 0) else {}
        self.unique_flat_map = {itemn: itemf for n, f in self.unique_map.items() for itemn, itemf in (self.foreign_models_map[n].unique_flat_map.items() if (n in self.foreign_models_map) else {n: f}.items())}
        # foreign
        self.foreign_unique_map = {n: self.foreign_models_map[n].unique_flat_map for n in self.foreign_field_map}
        self.foreign_flat = {n: f for uk, uv in self.foreign_unique_map.items() for n, f in uv.items()}
        # all fields needed to generate a record for this model, including finding dependencies by their unique values and record data
        self.dependent = set(self.foreign_flat) | (set(self.field_map) - set(self.foreign_field_map)) # - set(n for n, f in self.field_map.items() if f.model._meta.pk == f))
        self.dependent_non_null = {n for n in self.dependent if n in self.foreign_flat or (n in self.field_map and not self.field_map[n].null)}

    def print_hierarchy(self, depth=0):
        print(f"{'│   ' * depth}[\033[91m{self.name}\033[00m]")
        for n, m in self.foreign_models_map.items():
            print(f"{'│   ' * depth}├ {n}")
            m.print_hierarchy(depth=depth+1)


class Inserter(object):

    @staticmethod
    def _assert_table_exists(model):
        message = f"\n{'=' * 80}\nAre you sure you ran migrations on the database: \n\t$ python manage.py makemigrations\n\t$ python manage.py migrate --run-syncdb\n{'=' * 80}"
        assert model._meta.db_table in connection.introspection.table_names(), message

    def __init__(self, model: Type[Model]):
        Inserter._assert_table_exists(model)
        self.model = model
        self.info = ModelInfo(model)
        self.fields = self.info.field_map
        self.foreign_models = self.info.foreign_models_map
        self.foreign = self.info.foreign_field_map
        self.foreign_flat = self.info.foreign_flat
        self.unique = self.info.unique_flat_map
        self.dependent = self.info.dependent
        self.dependent_non_null = self.info.dependent_non_null
        self.foreign_unique = self.info.foreign_unique_map

    def log(self, log_func, message):
        log_func(f"[{self.model.__name__}]: {message}")

    # TODO: efficient, but uses a lot of memory...
    def _group(self, df: pd.DataFrame, cols=None) -> pd.DataFrame:
        cols = self.unique if cols is None else cols
        with Measure("group", logger.debug):
            self.log(logger.info, "Grouping Started...")
            # list of fields present in table
            if tuple(sorted(set(self.dependent))) != tuple(sorted(set(self.dependent) & set(df.columns))):
                raise VisibleError("Error, dependent field not all present in table")
            if tuple(sorted(set(cols))) != tuple(sorted(set(cols) & set(df.columns))):
                raise VisibleError("Error, group by cols not all present in table")
            # get all data
            table_column_indices = [df.columns.get_loc(c) for c in self.dependent]  # if handles missing columns
            table = df.values
            # get primary key data
            table_pk_column_indices = [df.columns.get_loc(c) for c in cols] # group by these columns
            table_pk = list(list(row) for row in table[:, table_pk_column_indices])  # inefficient
            # group by - finds unique entries by indices of fields
            self.log(logger.info, f"Grouping - {', '.join(cols)}")
            pk_unique, table_indices = np.unique(table_pk, axis=0, return_index=True)
            # get unique data specific to table
            grouped = table[table_indices][:, table_column_indices]
            grouped = pd.DataFrame(data=grouped, columns=self.dependent)
            # self explanatory
            self.log(logger.info, f"Grouped! Found {len(grouped)} unique entries")
            return grouped

    @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        with Measure("save", logger.info):
            if tuple(sorted(set(self.foreign_flat))) != tuple(sorted(set(self.foreign))):
                raise VisibleError("Does not supported foreign key that is not also a field of the table")
            else:
                with Measure("foreign", logger.debug):
                    # load all foreign key models
                    fk_objects = {k: {model_to_dict(item)[k]: item for item in fk_m.model.objects.all()} for k, fk_m in self.foreign_models.items()}
                    # list of fields present in table
                    present_fields = set(grouped)
                    print(present_fields)
                    # replace foreign key values with correct model
                    grouped = grouped.to_dict('records')
                    for fk in self.foreign:
                        for item in grouped:
                            item[fk] = fk_objects[fk][item[fk]]
            with Measure("normalising", logger.info):
                # convert or load models
                grouped = [self.model(**item) for item in grouped]
                existed = [m for m in self.model.objects.all()]
            with Measure("inserting", logger.info):
                # map tuple keys to objects
                grouped = {tuple(v for k, v in model_to_dict(m).items() if k in self.unique): m for m in grouped}
                existed = {tuple(v for k, v in model_to_dict(m).items() if k in self.unique): m for m in existed}
                # find differences
                insert = [grouped[key] for key in grouped.keys() - existed.keys()]
                # insert unique elements
                self.log(logger.info, f"Inserting {len(insert)}")
                self.model.objects.bulk_create(insert)
            return len(insert)

    def insert(self, df: pd.DataFrame) -> int:
        with Measure(f"{self.model.__name__}", logger.info):
            try:
                self.log(logger.info, f"BEFORE        - {len(self.model.objects.all())} entries")
                self.log(logger.info, f"FIELDS        - {sorted(self.fields)}")
                self.log(logger.info, f"UNIQUE        - {sorted(self.info.unique_map.keys())}")
                self.log(logger.info, f"UNIQUE (FLAT) - {sorted(self.info.unique_flat_map.keys())}")
                grouped = self._group(df)
                imported = self._save(grouped)
                self.log(logger.info, f"AFTER {len(self.model.objects.all())} entries")
            except Exception as e:
                self.log(logger.error, f"\033[91mERROR\033[0m")
                raise e
        print()
        return imported
