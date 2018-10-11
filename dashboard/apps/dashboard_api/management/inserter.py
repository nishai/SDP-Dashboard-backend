import logging
from typing import Type
import pandas as pd
import numpy as np
from django.db import connection, transaction
from django.db.models import Model, ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import model_to_dict
from dashboard.apps.dashboard_api.management.measure import Measure

logger = logging.getLogger('debug-import')


class Inserter(object):

    @staticmethod
    def _assert_table_exists(model):
        message = f"\n{'=' * 80}\nAre you sure you ran migrations on the database: \n\t$ python manage.py makemigrations\n\t$ python manage.py migrate --run-syncdb\n{'=' * 80}"
        assert model._meta.db_table in connection.introspection.table_names(), message

    def __init__(self, model: Type[Model]):
        Inserter._assert_table_exists(model)
        self.model = model
        self.pk = self.model._meta.pk
        # get fields
        self.fields = {f.name: f for f in model._meta.get_fields()}
        self.fields = {k: f for k, f in self.fields.items() if k != 'id' and not isinstance(f, ForeignObjectRel)}
        self.fields_unique = {f: self.fields[f] for f in self.model._meta.unique_together[0]} if len(self.model._meta.unique_together) > 0 else {}
        # get fields keys
        self.fks = {k: f for k, f in self.fields.items() if isinstance(f, ForeignKey)}
        self.pks = self.fields_unique if len(self.fields_unique) > 0 else ({k: f for k, f in self.fields.items()} if self.pk.name == 'id' else {self.pk.name: self.pk})


    # TODO: efficient, but uses a lot of memory...
    def _group(self, df: pd.DataFrame) -> pd.DataFrame:
        with Measure("group", logger.debug):
            logger.info(f"[{self.model.__name__}]: Grouping Started...")
            # list of fields present in table
            present_fields = set(c for c in self.fields.keys() if c in df.columns)
            # get all data
            table_column_indices = [df.columns.get_loc(c) for c in present_fields]  # if handles missing columns
            table = df.values
            # get primary key data
            table_pk_column_indices = [df.columns.get_loc(c) for c in self.pks.keys()]
            table_pk = list(list(row) for row in table[:, table_pk_column_indices])  # inefficient
            # group by - finds unique entries by indices of fields
            logger.info(f"[{self.model.__name__}]: Grouping - {', '.join(self.pks)}")
            pk_unique, table_indices = np.unique(table_pk, axis=0, return_index=True)
            # get unique data specific to table
            grouped = table[table_indices][:, table_column_indices]
            grouped = pd.DataFrame(data=grouped, columns=present_fields)
            # self explanatory
            logger.info(f"[{self.model.__name__}]: Grouped! Found {len(grouped)} unique entries")
            return grouped

    @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        with Measure("save", logger.debug):
            with Measure("foreign", logger.debug):
                # load all foreign key models
                fk_objects = {k: {model_to_dict(m)[k]: m for m in fk.foreign_related_fields[0].model.objects.all()} for
                              k, fk in self.fks.items()}
                # list of fields present in table
                present_fields = set(grouped)
                # replace foreign key values with correct model
                grouped = grouped.to_dict('records')
                for fk in self.fks.keys():
                    if fk in present_fields:
                        for item in grouped:
                            item[fk] = fk_objects[fk][item[fk]]
                    else:
                        logger.warning(f"[{self.model.__name__}]: \033[93mSKIPPING FK\033[0m: '{fk}' - (not present in import data) will be null")
            with Measure("normalising", logger.debug):
                # convert grouped to models
                grouped = [self.model(**item) for item in grouped]
                # load existing
                existed = [m for m in self.model.objects.all()]
            with Measure("inserting", logger.debug):
                # find differences
                grouped = {tuple(v for k, v in model_to_dict(m).items() if k in self.pks): m for m in grouped}
                existed = {tuple(v for k, v in model_to_dict(m).items() if k in self.pks): m for m in existed}
                insert = [grouped[key] for key in grouped.keys() - existed.keys()]
                # insert unique elements
                logger.info(f"[{self.model.__name__}]: Inserting {len(insert)}")
                self.model.objects.bulk_create(insert)
            return len(insert)

    def insert(self, df: pd.DataFrame) -> int:
        with Measure(f"{self.model.__name__}", logger.info):
            try:
                logger.info(f"[{self.model.__name__}]: Before {len(self.model.objects.all())} entries")
                logger.info(f"[{self.model.__name__}]: Fields - {', '.join(self.fields)}")
                logger.info(f"[{self.model.__name__}]: Pks - {', '.join(self.pks)}")
                grouped = self._group(df)
                imported = self._save(grouped)
                logger.info(f"[{self.model.__name__}]: After {len(self.model.objects.all())} entries")
            except Exception as e:
                logger.error(f"[{self.model.__name__}] \033[91mERROR\033[0m")
                raise e
        print()
        return imported
