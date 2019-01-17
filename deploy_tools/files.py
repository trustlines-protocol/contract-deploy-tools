import os
import fnmatch
import json
from typing import Dict


def find_files(dir: str, pattern: str):
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(dirpath, filename)


def ensure_path_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def write_compiled_contracts(compiled_contracts: Dict, compiled_contracts_asset_path: str):
    with open(compiled_contracts_asset_path, 'w') as file:
        json.dump(
            compiled_contracts,
            file,
            indent=4
        )
