import yaml
# import dill
from networksecurity.utilities.exception import NetworkSecurityException
from networksecurity.utilities.logger import logger
import os, sys
import pickle
import numpy as np


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def write_yaml_file(file_path: str, content: str, replace: bool=True):
    try:
        if replace and os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(
                content,
                file,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e