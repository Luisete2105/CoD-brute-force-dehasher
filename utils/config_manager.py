import json
import os
import logging
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.default_folder = os.path.dirname(os.path.abspath(__file__)).rsplit('gui', 1)[0]

    def load_config(self) -> dict:
        """
        Load configuration from config.json.
        Returns default config if file doesn't exist or is invalid.
        """
        default_config = {
            "selected_algorithms": [],
            "excluded_characters": [],
            "last_hashed_string": None,
            "disable_uncommon_combinations": False,
            "last_folder": self.default_folder
        }
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    logging.info(f"Loaded config: {config}")
                    return config
            logging.info("Config file not found, returning default config")
            return default_config
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            return default_config

    def save_brute_force_config(
        self,
        selected_algorithms: List[str],
        excluded_characters: List[str],
        last_string: Optional[str] = None,
        disable_uncommon_combinations: bool = False
    ) -> None:
        """
        Save brute force configuration to config.json.
        Preserves existing last_folder.
        """
        try:
            config = self.load_config()
            config.update({
                "selected_algorithms": selected_algorithms,
                "excluded_characters": excluded_characters,
                "last_hashed_string": last_string,
                "disable_uncommon_combinations": disable_uncommon_combinations
            })
            self.save_config(config)
            logging.info(f"Saved brute force config: {config}")
        except Exception as e:
            logging.error(f"Error saving brute force config: {str(e)}")

    def save_config(self, config: dict) -> None:
        """
        Save configuration to config.json.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logging.info(f"Saved config to {self.config_path}")
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")

    def get_folder(self) -> str:
        """
        Retrieve the last saved folder path from config.json.
        Returns default folder if not set.
        """
        config = self.load_config()
        folder = config.get("last_folder", self.default_folder)
        logging.info(f"Retrieved folder: {folder}")
        return folder

    def save_folder(self, folder: str) -> None:
        """
        Save a folder path to config.json.
        """
        try:
            config = self.load_config()
            config["last_folder"] = folder
            self.save_config(config)
            logging.info(f"Saved folder: {folder}")
        except Exception as e:
            logging.error(f"Error saving folder: {str(e)}")

    def get_brute_force_config(self) -> Tuple[List[str], List[str]]:
        """
        Retrieve brute force configuration (selected_algorithms, excluded_characters).
        Returns empty lists if not set.
        """
        config = self.load_config()
        selected_algorithms = config.get("selected_algorithms", [])
        excluded_characters = config.get("excluded_characters", [])
        logging.info(f"Retrieved brute force config: selected_algorithms={selected_algorithms}, excluded_characters={excluded_characters}")
        return selected_algorithms, excluded_characters