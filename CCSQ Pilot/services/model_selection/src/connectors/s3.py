import boto3

from pathlib import Path
from ..utils import get_config_settings, get_tmp_dir


class S3:
    def __init__(self):
        self.client = boto3.client('s3')

    def upload_file(self, filename, bucket, key):
        return self.client.upload_file(filename, bucket, key)

    def upload_fileobj(self, buffer, bucket, key):
        return self.client.upload_fileobj(buffer, bucket, key)

    def download_modeling_dataset_to_local_temp(self):
        settings = get_config_settings()

        measure_specific_filename = settings.get('MEASURE_SPECIFIC_FILENAME')

        bucket = settings.get('MODELING_DATASET_BUCKET')
        key = measure_specific_filename

        local_temp_dir = get_tmp_dir()
        Path(local_temp_dir).mkdir(parents=True, exist_ok=True)

        path = f"{local_temp_dir}/{key}"
        self.download_file(bucket, key, path)

    def download_file(self, bucket, key, path):
        with open(path, 'wb') as f:
            print(f"Downloading from {bucket}: {key} to {path}")
            self.client.download_fileobj(bucket, key, f)

