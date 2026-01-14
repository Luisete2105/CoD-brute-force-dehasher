# src/core/shared_data.py
class GameData:
    def __init__(self):
        self.hash_functions = {}  # type_name → hash_func

    def add_type(self, type_name: str, hash_func):
        self.hash_functions[type_name] = hash_func