import json
import os

user_settings = {}


def set_user_settings(_user_settings):
    global user_settings
    user_settings = _user_settings


def get_config_settings():
    file_directory = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(file_directory, '../../config.json')

    with open(config_path) as f:
        settings = json.load(f)

    return {**settings, **user_settings}
