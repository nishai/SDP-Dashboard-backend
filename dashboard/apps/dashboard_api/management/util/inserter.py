import logging
from pprint import pprint
from typing import Type
import pandas as pd
import numpy as np
from django.db import connection, transaction
from django.db.models import Model, ForeignKey, Field, AutoField
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import model_to_dict
from dashboard.apps.dashboard_api.management.util.measure import Measure

logger = logging.getLogger('debug-import')


class VisibleError(RuntimeError):
    def __init__(self, desc):
        super(VisibleError, self).__init__(f"\n{'=' * 80}\n\033[91m{desc}\n\033[00m{'=' * 80}")


class ModelInfo(object):

    def __init__(self, model: Type[Model]):
        # model
        self.model = model
        self.meta = self.model._meta
        self.name = self.meta.object_name  # self.meta.model_name
        # maps
        self.field_map = {f.name: f for f in self.meta.get_fields() if not isinstance(f, ForeignObjectRel) and not isinstance(f, AutoField) and f.name != 'id'}
        # hierarchy
        self.foreign_field_map = {n: f for n, f in self.field_map.items() if isinstance(f, ForeignKey)}
        self.foreign_models_map = {n: ModelInfo(f.related_model) for n, f in self.foreign_field_map.items()}
        # unique
        self.unique_map = {n: self.field_map[n] for n in self.meta.unique_together[0]} if (len(self.meta.unique_together) > 0) else {}
        self.unique_flat_map = {itemn: itemf for n, f in self.unique_map.items() for itemn, itemf in (self.foreign_models_map[n].unique_flat_map.items() if (n in self.foreign_models_map) else {n: f}.items())}
        # foreign
        self.foreign_unique_map = {n: self.foreign_models_map[n].unique_flat_map for n in self.foreign_field_map}
        self.foreign_flat = {n: f for uk, uv in self.foreign_unique_map.items() for n, f in uv.items()}
        # all fields needed to generate a record for this model, including finding dependencies by their unique values and record data
        self.dependent = set(self.foreign_flat) | (set(self.field_map) - set(self.foreign_field_map))
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

    @staticmethod
    def a_not_in_b(a, b):
        return set(a) - (set(a) & set(b))

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
            if len(self.a_not_in_b(self.dependent_non_null, df.columns)) > 0:
                raise VisibleError(f"Error, dependent fields '{sorted(self.a_not_in_b(self.dependent_non_null, df.columns))}' not present in table!")
            elif len(self.a_not_in_b(self.dependent, df.columns)) > 0:
                self.log(logger.warning, f"Some nullable fields '{sorted(self.a_not_in_b(self.dependent, df.columns))}' are missing from the table")
            if len(self.a_not_in_b(cols, df.columns)) > 0:
                raise VisibleError(f"Error, group by cols '{sorted(self.a_not_in_b(cols, df.columns))}' not present in table")
            # effective group by (just drop columns)
            group_by = [c for c in cols if c in self.dependent]
            self.log(logger.info, f"Grouping By: {group_by}")
            grouped = df.drop_duplicates(group_by)
            self.log(logger.info, f"Grouped! Found {len(grouped)} unique entries")
            return grouped

    @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        with Measure("save", logger.info):
            with Measure("foreign", logger.info):
                # lists of fields
                fks_virtual = set(self.foreign) - set(grouped)
                fks_present = set(self.foreign) - fks_virtual
                # convert grouping to dictionaries
                grouped = [dict(item) for item in grouped.to_dict('records')]
                # replace - missing
                with Measure("virtual", logger.debug):
                    for fk in fks_virtual:  # fks that are links, and therefore not in the table
                        # get fk meta
                        fk_unique_cols = tuple(sorted(self.foreign_unique[fk]))
                        # load data & map unique fields to objects
                        fk_unique_to_object = [(entry, model_to_dict(entry)) for entry in self.foreign_models[fk].model.objects.all()]
                        fk_unique_to_object = {tuple(item[k] for k in fk_unique_cols): entry for entry, item in fk_unique_to_object}
                        # replace
                        for item in grouped:
                            item[fk] = fk_unique_to_object[tuple(item[k] for k in fk_unique_cols)]
                # replace - present
                with Measure("present", logger.debug):
                    for fk in fks_present:
                        # load data
                        pk_to_object = {m.pk: m for m in self.foreign[fk].related_model.objects.all()}
                        # replace
                        try:
                            for item in grouped:
                                item[fk] = pk_to_object[item[fk]]
                        except KeyError as e:
                            raise VisibleError(f"Failed to retrieve foreign items for '{fk}', are you sure you have imported all the data's decencies?").with_traceback(e.__traceback__)
            with Measure("normalising", logger.debug):
                # remove flat fields, then convert or load model rows
                grouped = [{k: v for k, v in item.items() if k in self.info.field_map} for item in grouped]
                grouped = [self.model(**item) for item in grouped]
                existed = [m for m in self.model.objects.all()]
            with Measure("inserting", logger.debug):
                # map tuple keys to objects, and find differences between sets
                grouped = {tuple(model_to_dict(m, fields=self.info.unique_map).values()): m for m in grouped}
                existed = {tuple(model_to_dict(m, fields=self.info.unique_map).values()): m for m in existed}
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
                # drop bad cols
                df_old = df.where((pd.notnull(df)), None) # replace nan with none (side effect: everything is now an object)
                df = df_old.dropna(how='any', subset=self.dependent_non_null)
                if len(df_old) - len(df) > 0:
                    self.log(logger.info, f"Dropped {len(df_old) - len(df)} rows! Columns '{sorted(self.dependent_non_null)}' Break non-null requirement:\n{df_old[~df_old.isin(df)].dropna(how='all')}")
                del df_old
                # import
                grouped = self._group(df)
                imported = self._save(grouped)
                self.log(logger.info, f"AFTER {len(self.model.objects.all())} entries")
            except Exception as e:
                self.log(logger.error, f"\033[91mERROR\033[0m")
                raise e
        print()
        return imported
