import os

import boto3

from pathlib import Path
from ..utils import get_config_settings, get_measure_dir, get_consolidated_dir, get_tmp_dir


class S3:
    def __init__(self):
        self.client = boto3.client('s3')

    def upload_file(self, filename, bucket, key):
        return self.client.upload_file(filename, bucket, key)

    def upload_fileobj(self, buffer, bucket, key):
        return self.client.upload_fileobj(buffer, bucket, key)

    def upload_metadata_file(self):
        settings = get_config_settings()

        measure_specific_filename = settings.get('MEASURE_SPECIFIC_FILENAME')
        bucket = settings.get('MEASURE_SPECIFIC_DATA_BUCKET')

        consolidated_metadata_file_prefix = settings.get('consolidated_metadata_file_prefix')
        key = f"{consolidated_metadata_file_prefix}{measure_specific_filename}".replace('.csv', '.txt')
        tmp_dir = get_tmp_dir()
        path = f"{tmp_dir}/{key}"

        print(f'Uploading consolidated metadata to {bucket}: {key} from {path}')
        self.upload_file(path, bucket, key)

    def upload_consolidated_file(self):
        settings = get_config_settings()

        measure_specific_filename = settings.get('MEASURE_SPECIFIC_FILENAME')

        bucket = settings.get('MEASURE_SPECIFIC_DATA_BUCKET')
        key = measure_specific_filename

        measure_dir = get_consolidated_dir()
        path = f"{measure_dir}/{measure_specific_filename}"

        print(f'Uploading consolidated dataset to {bucket}: {key} from {path}')
        self.upload_file(path, bucket, key)

    def files_already_downloaded(self):
        local_temp_dir = get_measure_dir()
        return os.path.exists(local_temp_dir)

    def download_measure_files_to_local_temp(self):
        settings = get_config_settings()

        bucket = settings.get('FULL_MEASURE_DATA_BUCKET')
        prefix = settings.get('FULL_MEASURE_S3_PREFIX') + '/'

        local_temp_dir = get_measure_dir()
        Path(local_temp_dir).mkdir(parents=True, exist_ok=True)

        files = self.client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
        )

        self.process_files(files["Contents"], bucket, prefix, local_temp_dir)
        cont_token = files.get("NextContinuationToken")

        while cont_token:
            files = self.client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                ContinuationToken=cont_token,
            )
            self.process_files(files["Contents"], bucket, prefix, local_temp_dir)
            cont_token = files.get("NextContinuationToken")

    def process_files(self, files, bucket, prefix, local_path):
        for file in files:
            key = file["Key"]
            path = f'{local_path}/{key.split(prefix)[1]}'
            with open(path, 'wb') as f:
                print(f"Downloading from {bucket}: {key} to {path}")
                self.client.download_fileobj(bucket, key, f)
