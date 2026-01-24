import pickle


class use_pickel:
    def __init__(self, file_path, default_data=None):
        if default_data is None:
            default_data = {}
        self.file_path = file_path
        self.data = default_data

    def __enter__(self):
        try:
            with open(self.file_path, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = self.data
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.file_path, 'wb') as f:
            pickle.dump(self.data, f)
