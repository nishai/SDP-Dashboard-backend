from pprint import pprint
from typing import Dict, List, Type, Tuple
from django.db import transaction
import pandas as pd
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from dashboard.apps.dashboard_api.management.measure import Timer
from dashboard.apps.dashboard_api.models import StudentInfo, ProgramInfo, CourseStats, AverageYearMarks
from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.data_util import load_table
import numpy as np

logger = logging.getLogger('debug-import')


class Inserter(object):

    def __init__(self, model: Type[Model]):
        self.model = model
        # get pk
        self.pk = self.model._meta.pk
        # get fields
        self.fields = {f.name: f for f in model._meta.get_fields()}
        self.fields = {k: f for k, f in self.fields.items() if k != 'id' and not isinstance(f, ForeignObjectRel)}
        # get fields keys
        self.fks = {k: f for k, f in self.fields.items() if isinstance(f, ForeignKey)}
        self.pks = {k: f for k, f in self.fields.items()} if self.pk.name == 'id' else {self.pk.name: self.pk}

    def _group(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def _save(self, grouped: pd.DataFrame) -> int:

        fk_objects = dict()
        for fk, fk_field in self.fks.items():
            fk_unique = np.unique(grouped[fk].values)
            fk_model = fk_field.foreign_related_fields[0].model
            fk_objects[fk] = fk_model.objects.in_bulk(list(fk_unique))
            logger.info(f"[{self.model.__name__}]: Loaded Foreign Data: '{fk}' {len(fk_objects[fk])} ")

        logger.info(f"[{self.model.__name__}]: Replacing Foreign Data for {len(grouped)} entries")
        for fk, fk_index in [(fk, grouped.columns.get_loc(fk)) for fk in self.fks.keys()]:
            for i, value in enumerate(grouped.values[:, fk_index]):
                grouped.values[i, fk_index] = fk_objects[fk][value]

        logger.info(f"[{self.model.__name__}]: Converting To Common Format for {len(grouped)} entries")
        items = {}
        for row in grouped.values:
            item = self.model(**{k: v for k, v in zip(grouped.columns, row)})
            if item.pk is not None:
                items[item.pk] = item

        logger.info(f"[{self.model.__name__}]: Removing duplicates")
        stored = self.model.objects.in_bulk(items.keys())
        insert = {k: v for k, v in items.items() if k not in stored}

        logger.info(f"[{self.model.__name__}]: Saving records {len(insert)}")
        self.model.objects.bulk_create(insert.values())

        return len(insert)

    def insert(self, df: pd.DataFrame) -> int:
        grouped = self._group(df)
        return self._save(grouped)

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
        count += Inserter(ProgramInfo).insert(df)
        count += Inserter(StudentInfo).insert(df)
        count += Inserter(CourseStats).insert(df)
        count += Inserter(AverageYearMarks).insert(df)
        return count
