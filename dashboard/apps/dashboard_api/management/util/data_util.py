import logging
import os
from typing import Union, List

import pandas as pd

logger = logging.getLogger('debug-import')


def load_table(file: str, header=5, dataframe=False):
    ext = os.path.splitext(file)[1].lower()

    if ext == ".xlsx":
        df = pd.read_excel(file, index_col=None, header=header)
    elif ext == ".csv":
        df = pd.read_csv(file, index_col=None)
    else:
        raise Exception(f"Unsupported file extension: {ext}")

    # some excel files have hidden empty columns
    df = df.filter(regex='^(?!Unnamed:).*', axis=1)
    df = df.rename(lambda s: s.lower().replace(" ", "_").replace("_/_", "_"), axis='columns')

    return df if dataframe else df.to_dict()


def load_tables(files: List[str], merged=False, header=5, dataframe=False):
    # load and merge/append tables together
    records, total = None if merged else [], 0
    for file in files:
        logger.info(f"Loading: {file}")
        assert os.path.isfile(file)
        temp = load_table(file, header=header, dataframe=dataframe)
        total += len(temp)
        records = temp if records is None and merged else records.append(temp)  # merge/append

    logger.info(f"Loaded: {total} records from {len(files)} files")
    return records


def save_table(path: str, df: Union[List[dict], pd.DataFrame]):
    if type(df) is dict:
        df = pd.DataFrame(df)

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df.to_csv(path, header=True, index=False)
    else:
        raise Exception(f"Unsupported file extension: {ext}")
