import configparser
import os

class Config:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        self.config.read(self.config_file)

    def get(self, section, key, fallback=None):
        try:
            return self.config[section].get(key, fallback=fallback)
        except KeyError:
            raise KeyError(f'{key} not found in {self.config_file}')

