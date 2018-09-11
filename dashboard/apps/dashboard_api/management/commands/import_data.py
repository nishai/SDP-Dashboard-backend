from pprint import pprint
from typing import Dict, List, Type
from django.db import transaction
import pandas as pd
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from dashboard.apps.dashboard_api.models import StudentInfo, ProgramInfo, CourseStats, AverageYearMarks
from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.data_util import load_table

logger = logging.getLogger('debug-import')


class Inserter(object):

    def __init__(self, model: Type[Model]):
        self.model = model
        # get pk
        self.pk = self.model._meta.pk
        # get fields
        self.fields = {f.name: f for f in model._meta.get_fields()}
        self.fields = {k: f for k, f in self.fields.items() if f != 'id' and not isinstance(f, ForeignObjectRel)}
        # get fields keys
        self.fks = {k: f for k, f in self.fields.items() if isinstance(f, ForeignKey)}
        self.pks = {k: f for k, f in self.fields.items()} if self.pk.name == 'id' else {self.pk.name: self.pk}

    def _group(self, df: pd.DataFrame) -> List[Dict]:
        logger.info(f"[{self.model.__name__}]: Grouping...")
        logger.info(f"[{self.model.__name__}]: Grouping...")
        grouped = df.groupby(list(self.pks.keys()))
        entries = []
        for i, (key, dfgroup) in enumerate(grouped):
            if i % 1000 == 0:
                print(f"[{self.model.__name__}]: {i} of {len(grouped)}")
            row = dfgroup.iloc[0]  # get first row
            row = row.loc[self.fields]  # get needed fields from from
            entries += [row.to_dict()]  # convert to dict
        logger.info(f"[{self.model.__name__}]: {len(entries)} {list(self.pks.keys())}")
        return entries

    @transaction.atomic
    def _save(self, grouped: List[Dict]):
        logger.info(f"[{self.model.__name__}]: loading Foreign Data {len(self.fks)}")
        fk_objects = {}
        for fk, fk_field in self.fks.items():
            items = {item[fk] for item in grouped}
            fk_objects[fk] = fk_field.foreign_related_fields[0].model.objects.in_bulk(list(items))

        logger.info(f"[{self.model.__name__}]: Replacing Foreign Data {len(grouped)}")
        items = [self.model(**{k: fk_objects[k][v] if k in fk_objects else v for k, v in item.items()}) for item in
                 grouped]
        items = {item.pk: item for item in items}

        logger.info(f"[{self.model.__name__}]: Removing duplicates")
        stored = self.model.objects.in_bulk(items.keys())
        insert = {k: v for k, v in items.items() if k not in stored}
        update = {k: v for k, v in items.items() if k in stored}
        logger.info(f"[{self.model.__name__}]: Saving records {len(insert)}")
        self.model.objects.bulk_create(insert.values())

    def insert(self, df: pd.DataFrame):
        grouped = self._group(df)
        self._save(grouped)



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
        Inserter(ProgramInfo).insert(df)
        Inserter(StudentInfo).insert(df)
        Inserter(CourseStats).insert(df)
        Inserter(AverageYearMarks).insert(df)

        # logger.info("-----------------------------------------------------------------------")
        # logger.info("Inserting data from table to  models: ")
        # logger.info("-----------------------------------------------------------------------")
        #
        # sys.stdout.flush()
        # try:
        #     api_app = apps.get_app_config('dashboard_api')
        #     api_models = api_app.models.values()
        #
        #     pprint(api_app)
        #     pprint(api_models)
        # except:
        #     pass
        #
        #     for _model in api_models:
        #         logger.info("-----------------------------------------------------------------------")
        #         logger.info("Inserting data to model: " + _model.__name__)
        #         logger.info("-----------------------------------------------------------------------")
        #         sys.stdout.flush()
        #         _model_field_names = [f.name for f in _model._meta.get_fields()]
        #         logger.debug("model fields: " + str(_model_field_names))
        #         logger.debug("titles of excel table" + str(titles))
        #         sys.stdout.flush()
        #
        #         # check for foreign keys
        #         _model_field_objects = [f for f in _model._meta.get_fields()]
        #         foreign_key_fields_dict = {}
        #         for field in _model_field_objects:
        #             if field.__class__ is ForeignKey:
        #                 foreign_key_fields_dict[field.name] = field.related_model
        #         logger.debug("Foreign key fields are: " + str(foreign_key_fields_dict))
        #         sys.stdout.flush()
        #
        #         for row in data:
        #             _model_dict = {key: value for key, value in zip(titles, row) if key in _model_field_names}
        #             # adjust foreign key to their class
        #             for key in _model_dict:
        #                 if key in foreign_key_fields_dict:
        #                     _model_dict[key] = foreign_key_fields_dict[key].objects.get(pk=_model_dict[key])
        #
        #             try:
        #                 # insert to table
        #                 _model.objects.update_or_create(**_model_dict)
        #             except Exception as e:
        #                 logger.warning("error inserting to table, ignored and continued. error is: " + str(e))
        #                 pass
        #         logger.debug("model values: " + str(_model.objects.values()))
        #         sys.stdout.flush()
        #     return 0
        # except Exception as e:
        #     raise Exception("Error inserting data to database with error: " + str(e))
