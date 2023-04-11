import json
import os


def get_tmp_dir():
    settings = get_config_settings()
    local_download_dir = settings.get('LOCAL_TEMP_DIR')

    return f"{local_download_dir}"


def get_measure_dir():
    return f"{get_tmp_dir()}/split"


def get_consolidated_dir():
    return f"{get_tmp_dir()}/combined"


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
