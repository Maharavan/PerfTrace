import os
import yaml
from perftrace.constant import CONFIG_PATH, DEFAULT_CONFIG

class ConfigManager:

    @staticmethod
    def check_if_config_exists():
        """
        Ensure the config file exists. If not, create it from DEFAULT_CONFIG.
        """
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as cfg:
                yaml.dump(DEFAULT_CONFIG, cfg, default_flow_style=False, sort_keys=False)

    @staticmethod
    def load_config():
        """
        Load and return the YAML config as a dictionary.
        If file doesn't exist, auto-create from defaults.
        """
        ConfigManager.check_if_config_exists()

        with open(CONFIG_PATH, "r", encoding="utf-8") as cfg:
            loaded_data = yaml.safe_load(cfg) or {}
        
        return loaded_data

    @staticmethod
    def save_config(data):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as cfg:
            yaml.dump(data, cfg, default_flow_style=False, sort_keys=False)