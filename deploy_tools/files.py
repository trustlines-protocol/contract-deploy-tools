import os
import fnmatch
import json
from pathlib import Path
from typing import Dict


def find_files(dir: str, pattern: str):
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(dirpath, filename)


def ensure_path_for_file_exists(file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def write_pretty_json_asset(json_data: Dict, asset_path: str):
    with open(asset_path, "w") as file:
        json.dump(json_data, file, indent=4)


def write_minified_json_asset(json_data: Dict, compiled_contracts_asset_path: str):
    with open(compiled_contracts_asset_path, "w") as file:
        json.dump(json_data, file, separators=(",", ":"))
