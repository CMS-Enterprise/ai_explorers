###################################################
# feature_engineering
# Adds feature engineering to create 
# lags, differencing, and provider level means
###################################################
import os
import shutil

from .metadata import Metadata
from .connectors.s3 import S3
from .engineering import Engineering
from .utils import get_config_settings, set_user_settings


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    s3_client = S3()
    engineering = Engineering()

    s3_client.download_consolidated_measure_file_to_local_temp()
    engineering.run()
    engineering.save_df_locally()

    metadata = Metadata(engineering.df)
    metadata.generate()
    metadata.write_log_locally()

    s3_client.upload_engineered_file()
    s3_client.upload_metadata_file()

    save_modeling_dataset_path = settings.get('save_modeling_dataset_path')
    if save_modeling_dataset_path is not None and len(save_modeling_dataset_path) > 0:
        engineering.save_df_as_csv(save_modeling_dataset_path)

    clean_up()


def clean_up():
    settings = get_config_settings()

    local_temp_dir = settings.get('LOCAL_TEMP_DIR')

    if os.path.exists(local_temp_dir):
        shutil.rmtree(local_temp_dir)


if __name__ == '__main__':
    main(None)
