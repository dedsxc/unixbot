import configparser
from pathlib import Path

def load_config(file_path=None):
    # Avoid ambiguous characters in config file
    config = configparser.ConfigParser(interpolation=None)
    config.read(file_path or Path(__file__).parent.parent / "config.ini")
    return config

config = load_config()
