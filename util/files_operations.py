import json
import os


def load_json(file_path, default_json):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    else:
        return default_json


def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
