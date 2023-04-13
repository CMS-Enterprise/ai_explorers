import json
import os


def get_file_paths_and_names_from_downloaded_measure_files():
    local_download_dir = get_full_local_download_path()

    file_paths = []
    dir_list = os.listdir(local_download_dir)
    for file in dir_list:
        path = f'{local_download_dir}/{file}'
        file_paths.append((path, file))

    file_paths.sort()
    return file_paths


def get_full_local_download_path():
    settings = get_config_settings()

    local_download_dir = settings.get('LOCAL_DOWNLOAD_DIR')
    sharepoint_measure_dir = settings.get('SHAREPOINT_MEASURE_DIR')

    return f"{local_download_dir}/{sharepoint_measure_dir}"


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
