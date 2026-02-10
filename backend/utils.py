import json
import os
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _get_file_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)

def read_json(filename: str) -> List[Dict[str, Any]]:
    path = _get_file_path(filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_json(filename: str, data: List[Dict[str, Any]]):
    path = _get_file_path(filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def append_json(filename: str, item: Dict[str, Any]):
    data = read_json(filename)
    data.append(item)
    write_json(filename, data)

def update_json(filename: str, key: str, value: Any, update_data: Dict[str, Any]):
    data = read_json(filename)
    for i, item in enumerate(data):
        if item.get(key) == value:
            data[i].update(update_data)
            write_json(filename, data)
            return True
    return False

def get_by_id(filename: str, id_value: str) -> Dict[str, Any] | None:
    data = read_json(filename)
    for item in data:
        if item.get("id") == id_value:
            return item
    return None
