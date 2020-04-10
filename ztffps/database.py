#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause
import os, logging, collections
from typing import Union, Any, Sequence, Tuple
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


def read_database(
    ztf_objects: Union[list, str], requested_data: Union[list, str], logger=None
) -> Any:
    """
    Returns entries in metadata database for all ztf_objects given that are requested in requested_data
    """
    from pipeline import METADATA

    if logger is None:
        logger = logging.getLogger("database")

    assert isinstance(requested_data, list) or isinstance(requested_data, str)
    assert isinstance(ztf_objects, list) or isinstance(ztf_objects, str)

    metadata_db = TinyDB(os.path.join(METADATA, "meta_database.json"))

    if isinstance(ztf_objects, str):
        ztf_objects = [ztf_objects]
    if isinstance(requested_data, str):
        requested_data = [requested_data]

    dict_for_return_values = collections.defaultdict(list)
    for i, name in enumerate(ztf_objects):
        query = metadata_db.search(Query().name == name)
        if query:
            for entry in requested_data:
                if query[0].get(entry, None) is not None:
                    dict_for_return_values[entry].append(query[0][entry])
                else:
                    dict_for_return_values[entry].append(None)
        else:
            logger.warning(f"\nNo entry found for {name}, will return none")
            for entry in requested_data:
                dict_for_return_values[entry].append(None)

    metadata_db.close()

    return dict_for_return_values


def update_database(
    ztf_objects: Union[list, str], data_to_update: dict, logger=None
) -> Any:
    """
    Updates metadata database for all ztf_objects given with data in data_to_update (in form of a dictionary)
    """
    from pipeline import METADATA

    if logger is None:
        logger = logging.getLogger("database")

    assert isinstance(data_to_update, dict)
    assert isinstance(ztf_objects, list) or isinstance(ztf_objects, str)

    metadata_db = TinyDB(
        os.path.join(METADATA, "meta_database.json"),
        storage=CachingMiddleware(JSONStorage),
    )

    if isinstance(ztf_objects, str):
        ztf_objects = [ztf_objects]

    dict_for_return_values = collections.defaultdict()

    for i, name in enumerate(ztf_objects):
        upsert_dict = {"name": name}

        for key, value in data_to_update.items():

            if type(value) != list:
                upsert_dict.update({key: value})
            else:
                upsert_dict.update({key: value[i]})

        metadata_db.upsert(
            upsert_dict, Query().name == name,
        )

    metadata_db.close()
