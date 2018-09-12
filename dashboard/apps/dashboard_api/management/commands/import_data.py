from typing import Dict, List, Type, Tuple
from django.db import transaction, IntegrityError, connection
import pandas as pd
from django.db.models import Model, CharField
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel

from dashboard.apps.dashboard_api.management.measure import Timer
from dashboard.apps.dashboard_api.models import StudentInfo, ProgramInfo, CourseStats, AverageYearMarks, RawStudentModel
from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.data_util import load_table
import numpy as np


logger = logging.getLogger('debug-import')

class Inserter(object):

    @staticmethod
    def _assert_table_exists(model):
        message = f"\n{'='*80}\nAre you sure you ran migrations on the database: \n\t$ python manage.py makemigrations\n\t$ python manage.py migrate --run-syncdb\n{'='*80}"
        assert model._meta.db_table in connection.introspection.table_names(), message

    def __init__(self, model: Type[Model]):
        Inserter._assert_table_exists(model)
        self.model = model
        self.pk = self.model._meta.pk
        # get fields
        self.fields = {f.name: f for f in model._meta.get_fields()}
        self.fields = {k: f for k, f in self.fields.items() if k != 'id' and not isinstance(f, ForeignObjectRel)}
        self.fields_unique = {f: self.fields[f] for f in self.model._meta.unique_together[0]}
        # get fields keys
        self.fks = {k: f for k, f in self.fields.items() if isinstance(f, ForeignKey)}
        self.pks = self.fields_unique if len(self.fields_unique) > 0 else ({k: f for k, f in self.fields.items()} if self.pk.name == 'id' else {self.pk.name: self.pk})
        # converters
        def get_converter(converter): # TODO: fix
            def c(x):
                val = converter(x)
                return None if val == 'nan' else val
            return c
        self.field_converters = {k: get_converter(v.to_python) for k, v in self.fields.items()}

    # TODO: efficient, but uses a lot of memory...
    def _group(self, df: pd.DataFrame) -> pd.DataFrame:
        with Timer("group", logger.debug):
            logger.info(f"[{self.model.__name__}]: Grouping...")
            # get all data
            table_column_indices = [df.columns.get_loc(c) for c in self.fields.keys()]
            table = df.values
            # get primary key data
            table_pk_column_indices = [df.columns.get_loc(c) for c in self.pks.keys()]
            table_pk = list(list(row) for row in table[:, table_pk_column_indices])  # inefficient
            # get indices of unique primary keys
            pk_unique, table_indices = np.unique(table_pk, axis=0, return_index=True)
            # get unique data specific to table
            grouped = table[table_indices][:, table_column_indices]
            grouped = pd.DataFrame(data=grouped, columns=self.fields.keys())
            # self explanatory
            logger.info(f"[{self.model.__name__}]: Grouped! Found {len(grouped)} unique entries")
            return grouped

    # @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        with Timer("save", logger.debug):
            # load all foreign data that corresponds to foreign keys in this model
            fk_objects = dict()
            for fk, fk_field in self.fks.items():
                fk_unique = np.unique(grouped[fk].values)
                fk_model = fk_field.foreign_related_fields[0].model
                fk_objects[fk] = fk_model.objects.in_bulk(list(fk_unique))
                logger.info(f"[{self.model.__name__}]: Loaded Foreign Data: '{fk}' {len(fk_objects[fk])} ")
            # Foreign key fields need to be instances of the foreign models themselves
            logger.info(f"[{self.model.__name__}]: Replacing Foreign Data for {len(grouped)} entries")
            for fk, fk_index in [(fk, grouped.columns.get_loc(fk)) for fk in self.fks.keys()]:
                for i, value in enumerate(grouped.values[:, fk_index]):
                    grouped.values[i, fk_index] = fk_objects[fk][value]
            # converting values
            with Timer("convert", logger.debug):
                logger.info(f"[{self.model.__name__}]: Converting {len(grouped)} entries")
                items = [{k: v for k, v in zip(grouped.columns, row)} for row in grouped.values]
            # insert values
            with Timer("insertion", logger.debug):
                logger.info(f"[{self.model.__name__}]: Inserting {len(grouped)} entries")
                count, updated, manual = 0, 0, True
                if len(self.model.objects.all()) == 0:  # insert for the first time (FAST)
                    try:
                        objs = [self.model(**item) for item in items]
                        self.model.objects.bulk_create(objs)
                        manual, count = False, len(items)
                    except Exception as e:
                        logger.debug(e)
                        logger.info("Failed to import items in one go, falling back to manual insertion.")
                if manual:  # insert mode if table is not empty or there was an error (MUCH SLOWER)
                    for i, item in enumerate(items):
                        try:
                            # TODO: add transaction support. This is way too slow
                            obj, created = self.model.objects.get_or_create(**item)
                            if created:
                                count += 1
                            else:
                                updated += 1
                        except Exception as e:
                            pass
                        if i % 1000 == 0:
                            print(f"{round(i/len(items)*100*100)/100}%", end=" ", flush=True)
                    print("100%")
                logger.info(f"[{self.model.__name__}]: Inserted {count} of {len(items)} entries - Updated {updated} - Error {len(items)-count-updated}")
            return count

    def insert(self, df: pd.DataFrame) -> int:
        with Timer(f"{self.model.__name__}", logger.info):
            logger.info(f"[{self.model.__name__}]: Before {len(self.model.objects.all())} entries")
            grouped = self._group(df)
            imported = self._save(grouped)
            logger.info(f"[{self.model.__name__}]: After {len(self.model.objects.all())} entries")
        print()
        return imported

class Command(BaseCommand):
    help = 'Imports data from excel_import/excel_files/ into the database'

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')

    def handle(self, *args, **options):
        imported = 0
        for file in options['files']:
            logger.info(f"Importing: {file}")
            assert os.path.isfile(file)
            df = load_table(file, dataframe=True)
            imported += self.import_table(df)
        logger.info(f"Imported: {imported} records from {len(options['files'])} files")

    def import_table(self, df: pd.DataFrame):
        logger.info("Importing")

        count = 0
        # count += Inserter(RawStudentModel).insert(df)
        count += Inserter(ProgramInfo).insert(df)
        count += Inserter(StudentInfo).insert(df)
        count += Inserter(CourseStats).insert(df)
        count += Inserter(AverageYearMarks).insert(df)
        return count
