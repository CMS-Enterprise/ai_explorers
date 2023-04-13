import boto3


class EFS:
    def __init__(self):
        self.client = boto3.client('efs')
