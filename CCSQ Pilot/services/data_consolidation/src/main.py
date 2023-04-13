###################################################
# data_consolidation
# consolidates data from AWS S3 buckets
###################################################

import os
import shutil
from .connectors.s3 import S3
from .consolidation import Consolidation
from .metadata import Metadata
from .utils import get_config_settings, set_user_settings


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    s3_client = S3()
    consolidation = Consolidation()

    files_already_downloaded = s3_client.files_already_downloaded()
    download_once = settings.get('DOWNLOAD_CSV_ONCE')
    if not download_once:
        s3_client.download_measure_files_to_local_temp()
    elif not files_already_downloaded:
        s3_client.download_measure_files_to_local_temp()

    consolidation.consolidate()
    consolidation.save_df_locally()

    metadata_generator = Metadata(consolidation.df)
    metadata_generator.generate()
    metadata_generator.write_log_locally()

    s3_client.upload_consolidated_file()
    s3_client.upload_metadata_file()

    dont_clean = settings.get('KEEP_CSV_AFTER_CONSOLIDATION')
    if not dont_clean:
        clean_up()


def clean_up():
    settings = get_config_settings()

    local_temp_dir = settings.get('LOCAL_TEMP_DIR')
    if os.path.exists(local_temp_dir):
        shutil.rmtree(local_temp_dir)


if __name__ == '__main__':
    main(None)
