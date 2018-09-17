from typing import Type
from django.db import transaction, connection
import pandas as pd
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import model_to_dict

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

    @transaction.atomic
    def _save(self, grouped: pd.DataFrame) -> int:
        with Timer("save", logger.debug):
            with Timer("foreign", logger.debug):
                # load all foreign key models
                fk_objects = {k: {model_to_dict(m)[k]: m for m in fk.foreign_related_fields[0].model.objects.all()} for k, fk in self.fks.items()}
                # replace foreign key values with correct model
                grouped = grouped.to_dict('records')
                for fk in self.fks.keys():
                    for item in grouped:
                        item[fk] = fk_objects[fk][item[fk]]
            with Timer("normalising", logger.debug):
                # convert grouped to models
                grouped = [self.model(**item) for item in grouped]
                # load existing
                existed = [m for m in self.model.objects.all()]
            with Timer("inserting", logger.debug):
                # find differences
                grouped = {tuple(v for k, v in model_to_dict(m).items() if k in self.pks): m for m in grouped}
                existed = {tuple(v for k, v in model_to_dict(m).items() if k in self.pks): m for m in existed}
                insert = [grouped[key] for key in grouped.keys() - existed.keys()]
                # insert unique elements
                logger.info(f"[{self.model.__name__}]: Inserting {len(insert)}")
                self.model.objects.bulk_create(insert)
            return len(insert)

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

        count += Inserter(RawStudentModel).insert(df)
        count += Inserter(ProgramInfo).insert(df)
        count += Inserter(StudentInfo).insert(df)
        count += Inserter(CourseStats).insert(df)
        count += Inserter(AverageYearMarks).insert(df)
        return count
