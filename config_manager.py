import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.selected_folder = ""
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.selected_folder = config.get("selected_folder", "")
            else:
                self.selected_folder = ""
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.selected_folder = ""

    def save_config(self, folder):
        try:
            config = {"selected_folder": folder}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.selected_folder = folder
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get_folder(self):
        return self.selected_folder

# Compatibility functions for older code
def read_last_folder_path():
    config = ConfigManager()
    return config.get_folder()

def write_last_folder_path(folder):
    config = ConfigManager()
    config.save_config(folder)