import json
import os

class ConfigManager:
    def __init__(self):
        # Set settings.json in the root folder (same as main_cod_script_manager.py)
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.json")
        self.selected_folder = ""
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.selected_folder = config.get("last_folder", "")
            else:
                self.selected_folder = ""
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            with open("debug.log", 'a', encoding='utf-8') as f:
                f.write(f"Error loading config: {str(e)}\n")
            self.selected_folder = ""

    def save_config(self, folder):
        try:
            config = {"last_folder": folder}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.selected_folder = folder
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            with open("debug.log", 'a', encoding='utf-8') as f:
                f.write(f"Error saving config: {str(e)}\n")

    def get_folder(self):
        return self.selected_folder

def read_last_folder_path():
    config = ConfigManager()
    return config.get_folder()

def write_last_folder_path(folder):
    config = ConfigManager()
    config.save_config(folder)