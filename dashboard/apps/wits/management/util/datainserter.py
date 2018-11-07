import logging
from typing import Type
import pandas as pd
from django.db import connection, transaction
from django.db.models import Model
from django.forms import model_to_dict

from dashboard.shared.errors import VisibleError
from dashboard.shared.measure import Measure
from dashboard.apps.wits.management.util.modelinfo import ModelInfo

logger = logging.getLogger('debug-import')


class Inserter(object):
    """
    Helper class to transform, normalize data found in a flat table.
    Then in memory find duplicates and loading dependencies from necessary Models if foreign keys exist.
    """

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

    def log(self, log_func, message):
        log_func(f"[{self.model.__name__}]: {message}")


    def _group(self, df: pd.DataFrame, cols=None) -> pd.DataFrame:
        """
        Groups a flat table by the specified columns/composite keys,
        by dropping repeated data by placing a unique constraint on those columns.
        TODO: add function to resolve repeated data after grouping.
        TODO: Might use a lot of memory.
        """
        cols = self.info.unique_flat_map if cols is None else cols
        with Measure("group", logger.debug):
            self.log(logger.info, "Grouping Started...")
            # list of fields present in table
            if len(self.a_not_in_b(self.info.dependent_non_null, df.columns)) > 0:
                raise VisibleError(f"Error, dependent fields '{sorted(self.a_not_in_b(self.info.dependent_non_null, df.columns))}' not present in table!")
            elif len(self.a_not_in_b(self.info.dependent, df.columns)) > 0:
                self.log(logger.warning, f"Some nullable fields '{sorted(self.a_not_in_b(self.info.dependent, df.columns))}' are missing from the table")
            if len(self.a_not_in_b(cols, df.columns)) > 0:
                raise VisibleError(f"Error, group by cols '{sorted(self.a_not_in_b(cols, df.columns))}' not present in table")
            # effective group by (just drop columns)
            group_by = [c for c in cols if c in self.info.dependent]
            self.log(logger.info, f"Grouping By: {group_by}")
            grouped = df.drop_duplicates(group_by)
            self.log(logger.info, f"Grouped! Found {len(grouped)} unique entries")
            return grouped

    @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        """
        Insert data, loading foreign key data if necessary.
        Finds and removes duplicates in memory.
        """
        with Measure("save", logger.info):
            with Measure("foreign", logger.info):
                # lists of fields
                fks_virtual = set(self.info.foreign_field_map) - set(grouped)
                fks_present = set(self.info.foreign_field_map) - fks_virtual
                # convert grouping to dictionaries
                grouped = [dict(item) for item in grouped.to_dict('records')]
                # replace - missing
                with Measure("virtual", logger.debug):
                    for fk in fks_virtual:  # fks that are links, and therefore not in the table
                        # get fk meta
                        fk_unique_cols = tuple(sorted(self.info.foreign_unique_map[fk]))
                        # load data & map unique fields to objects
                        fk_unique_to_object = [(entry, model_to_dict(entry)) for entry in self.info.foreign_models_map[fk].model.objects.all()]
                        fk_unique_to_object = {tuple(item[k] for k in fk_unique_cols): entry for entry, item in fk_unique_to_object}
                        # replace
                        try:
                            for item in grouped:
                                item[fk] = fk_unique_to_object[tuple(item[k] for k in fk_unique_cols)]
                        except KeyError as e:
                            raise VisibleError(f"Failed to retrieve foreign items for '{fk}' ({sorted(self.info.foreign_unique_map[fk])}), are you sure you have imported all the data's decencies, and that the data does not contain nulls/blanks?").with_traceback(e.__traceback__)
                # replace - present
                with Measure("present", logger.debug):
                    for fk in fks_present:
                        # load data
                        pk_to_object = {m.pk: m for m in self.info.foreign_field_map[fk].related_model.objects.all()}
                        # replace
                        try:
                            for item in grouped:
                                item[fk] = pk_to_object[item[fk]]
                        except KeyError as e:
                            raise VisibleError(f"Failed to retrieve foreign items for '{fk}', are you sure you have imported all the data's decencies, and that the data does not contain nulls/blanks?").with_traceback(e.__traceback__)
            with Measure("normalising", logger.debug):
                # remove flat fields, then convert or load model rows
                grouped = [{k: v for k, v in item.items() if k in self.info.field_map} for item in grouped]
                grouped = [self.model(**item) for item in grouped]
                existed = [m for m in self.model.objects.all()]
            with Measure("inserting", logger.debug):
                # map tuple keys to objects, and find differences between sets
                grouped = {tuple(model_to_dict(m, fields=self.info.unique_map).values()): m for m in grouped}
                existed = {tuple(model_to_dict(m, fields=self.info.unique_map).values()): m for m in existed}
                if len(grouped) > 0 and len(existed) > 0:
                    types_grouped, types_existed = tuple(type(val) for val in list(grouped.keys())[0]), tuple(type(val) for val in list(existed.keys())[0])
                    if types_grouped != types_existed:
                        logger.warning(f"Types of imported keys differ from database. Are you sure the model field types are appropriate? {[t.__name__ for t in types_existed]} not {[t.__name__ for t in types_grouped]} for {list(self.info.unique_map)}")
                insert = [grouped[key] for key in grouped.keys() - existed.keys()]
                # insert unique elements
                self.log(logger.info, f"Inserting {len(insert)}")
                self.model.objects.bulk_create(insert)
            return len(insert)

    def insert(self, df: pd.DataFrame) -> int:
        print()
        self.info.print_hierarchy()
        print()
        with Measure(f"{self.model.__name__}", logger.info):
            try:
                self.log(logger.info, f"BEFORE        - {len(self.model.objects.all())} entries")
                self.log(logger.info, f"FIELDS        - {sorted(self.info.field_map)}")
                self.log(logger.info, f"UNIQUE        - {sorted(self.info.unique_map.keys())}")
                self.log(logger.info, f"UNIQUE (FLAT) - {sorted(self.info.unique_flat_map.keys())}")
                # drop bad cols
                df_old = df.where((pd.notnull(df)), None)  # replace nan with none (side effect: everything is now an object)
                df = df_old.dropna(how='any', subset=self.info.dependent_non_null)
                if len(df_old) - len(df) > 0:
                    self.log(logger.info, f"Dropped {len(df_old) - len(df)} rows! Columns '{sorted(self.info.dependent_non_null)}' Break non-null requirement:\n{df_old[~df_old.isin(df)].dropna(how='all')}")
                del df_old
                # import
                grouped = self._group(df)
                imported = self._save(grouped)
                self.log(logger.info, f"AFTER {len(self.model.objects.all())} entries")
            except Exception as e:
                self.log(logger.error, f"\033[91mERROR\033[0m")
                raise e
        return imported