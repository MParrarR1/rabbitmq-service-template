import json
import logging
import os


class ConfigParser():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_path = "config.json"
        self.config_dict = self.config_to_dict()

    def config_to_dict(self):
        try:
            with open(self.config_path) as config_file:
                config = json.load(config_file)
        except Exception as e:
            self.logger.exception(f"Failed to load config file, error: {e}")
            raise ValueError("Config File Not found")
        for _, second_level_config in config.items():
            for key, value in second_level_config.items():
                if isinstance(value, str) and value.startswith("$"):
                    env_value = os.environ.get(value[1:])
                    if not env_value:
                        raise ValueError(f"Value for config {key} pointing to env variable {value} Not found")
                    second_level_config[key] = env_value
        return config


config = ConfigParser().config_dict
