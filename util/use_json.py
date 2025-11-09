from util.files_operations import load_json, write_json


class use_json:
    def __init__(self, file_path, default_json=None):
        if default_json is None:
            default_json = {}
        self.file_path = file_path
        self.json_data = default_json

    def __enter__(self):
        try:
            self.json_data = load_json(self.file_path, self.json_data)
        except FileNotFoundError:
            self.json_data = self.json_data
        return self.json_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            write_json(self.file_path, self.json_data)
