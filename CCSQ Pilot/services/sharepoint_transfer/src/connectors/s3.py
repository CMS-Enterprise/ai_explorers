import boto3

from ..utils import get_config_settings


class S3:
    def __init__(self):
        self.client = boto3.client('s3')

    def upload_file(self, filename, bucket, key):
        return self.client.upload_file(filename, bucket, key)

    def upload_fileobj(self, buffer, bucket, key):
        return self.client.upload_fileobj(buffer, bucket, key)

    def upload_measure_files_to_s3(self, file_paths_and_names):
        settings = get_config_settings()

        bucket = settings.get('FULL_MEASURE_DATA_BUCKET')
        prefix = settings.get('FULL_MEASURE_S3_PREFIX')

        file_paths_and_names = list(filter(lambda file: '.csv' in file[1], file_paths_and_names))
        for (path, filename) in file_paths_and_names:
            key = f"{prefix}/{filename}"
            print(f'Uploading to {bucket}: {key}')
            self.upload_file(path, bucket, key)
