from pprint import pprint
from typing import Dict, List, Type, Tuple
from django.db import transaction
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
        # converters
        def get_converter(converter): # TODO: fix
            def c(x):
                val = converter(x)
                return None if val == 'nan' else val
            return c
        self.field_converters = {k: get_converter(v.to_python) for k, v in self.fields.items()}

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

    def _save(self, grouped: pd.DataFrame) -> int:
        with Timer("save", logger.debug):
            columns = list(grouped.columns.values)
            pk_column_indices = [grouped.columns.get_loc(c) for c in self.pks.keys()]
            converters = [self.field_converters[k] for k in columns]
            # normalise importing values
            grouped_list = [tuple(converter(e) for e, converter in zip(row, converters)) for row in grouped.values]
            grouped_dict = {tuple(row[i] for i in pk_column_indices): row for row in grouped_list}
            # normalise existing values
            existing_values = self.model.objects.all().values()
            pprint(list(existing_values))
            existing_df = pd.DataFrame(list(existing_values))
            existing_df = existing_df.rename(lambda x: x.rstrip('_id'), axis='columns')
            existing_df = existing_df.drop(columns='id', errors='ignore')
            existing_df = existing_df[columns]
            existing_list = [tuple(converter(e) for e, converter in zip(row, converters)) for row in existing_df.values]
            existing_dict = {tuple(row[i] for i in pk_column_indices): row for row in existing_list}
            # find values that we need to import
            items = [{k: v for k, v in zip(columns, grouped_dict[key])} for key in list(set(grouped_dict.keys()) - set(existing_dict.keys()))]
            # load all foreign data that corresponds to foreign keys in this model
            fk_objects = dict()
            for fk, fk_field in self.fks.items():
                fk_unique = list(set(item[fk] for item in items))
                fk_model = fk_field.foreign_related_fields[0].model
                fk_objects[fk] = fk_model.objects.in_bulk(fk_unique)
                logger.info(f"[{self.model.__name__}]: Loaded Foreign Data: '{fk}' {len(fk_objects[fk])} ")
            # Foreign key fields need to be instances of the foreign models themselves
            logger.info(f"[{self.model.__name__}]: Replacing Foreign Data for {len(grouped)} entries")
            for fk in self.fks.keys():
                for item in items:
                    item[fk] = fk_objects[fk][item[fk]]
            # bulk_create only accepts a list instances of a model
            logger.info(f"[{self.model.__name__}]: Converting To Common Format for {len(grouped)} entries")
            insert = [self.model(**item) for item in items]
            # insert data into the table
            logger.info(f"[{self.model.__name__}]: Saving records {len(insert)}")
            self.model.objects.bulk_create(insert)
            # return the insert count
            return len(insert)

    def insert(self, df: pd.DataFrame) -> int:
        with Timer(f"{self.model.__name__}", logger.info):
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
        # count += Inserter(RawStudentModel).insert(df)
        count += Inserter(ProgramInfo).insert(df)
        count += Inserter(StudentInfo).insert(df)
        count += Inserter(CourseStats).insert(df)
        count += Inserter(AverageYearMarks).insert(df)
        return count
