###################################################
# sharepoint_transfer
# Transfers data frome sharepoint
###################################################

import os
import shutil
from .connectors.sharepoint import Sharepoint
from .connectors.s3 import S3
from .utils import get_file_paths_and_names_from_downloaded_measure_files, get_full_local_download_path, \
    get_config_settings, set_user_settings


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    s3_client = S3()
    sharepoint_conn = Sharepoint()

    sharepoint_conn.download_measure_files_to_local_path(get_full_local_download_path())
    s3_client.upload_measure_files_to_s3(get_file_paths_and_names_from_downloaded_measure_files())
    clean_up()


def clean_up():
    settings = get_config_settings()

    local_download_dir = settings.get('LOCAL_DOWNLOAD_DIR')
    if os.path.exists(local_download_dir):
        shutil.rmtree(local_download_dir)


if __name__ == '__main__':
    main(None)
