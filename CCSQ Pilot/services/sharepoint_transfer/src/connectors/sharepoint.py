import os
from pathlib import Path
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

from ..utils import get_config_settings


class Sharepoint:
    ctx: ClientContext
    AUTH_MODES = {
        'CLIENT': 'client',
        'USER': 'user'
    }

    def __init__(self):
        settings = get_config_settings()

        self.tenant_prefix = settings.get('SHAREPOINT_TENANT_PREFIX')
        self.auth_mode = settings.get('SHAREPOINT_AUTH_MODE')
        self.measure_source_dir = settings.get('SHAREPOINT_MEASURES_SOURCE_DIR')
        self.measure_dir = settings.get('SHAREPOINT_MEASURE_DIR')

        self.source_dir = f"{self.measure_source_dir}/{self.measure_dir}"

        if self.auth_mode == self.AUTH_MODES['CLIENT']:
            # only load these variables in memory if it's client mode
            # to prevent unnecessary protected data from being loaded
            self.client_id = settings.get('SHAREPOINT_CLIENT_ID')
            self.secret = settings.get('SHAREPOINT_SECRET')

            self.setup_sharepoint_context_using_client_credentials()
            return

        if self.auth_mode == self.AUTH_MODES['USER']:
            # only load these variables in memory if it's user mode
            # to prevent unnecessary protected data from being loaded
            self.username = os.getenv('SHAREPOINT_USERNAME')
            self.password = os.getenv('SHAREPOINT_PASSWORD')

            if self.username is None:
                raise Exception('Missing env var SHAREPOINT_USERNAME for sharepoint user auth_mode')

            if self.password is None:
                raise Exception('Missing env var SHAREPOINT_PASSWORD for sharepoint user auth_mode')

            self.setup_sharepoint_context_using_user_credentials()
            return

        raise Exception(f'Unknown sharepoint_auth_mode {self.auth_mode}; expected "client" or "user"')

    def set_source_dir(self, source_dir):
        self.source_dir = source_dir

    def setup_sharepoint_context_using_user_credentials(self):
        sharepoint_url = f'https://{self.tenant_prefix}.sharepoint.com/sites/HAIP'
        user_credentials = UserCredential(self.username, self.password)
        self.ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)

    def setup_sharepoint_context_using_client_credentials(self):
        sharepoint_url = f'https://{self.tenant_prefix}.sharepoint.com'
        client_credentials = ClientCredential(self.client_id, self.secret)
        self.ctx = ClientContext(sharepoint_url).with_credentials(client_credentials)

    def get_measures_files_obj(self, directory: str = None):
        directory = self.source_dir if directory is None else directory

        contents = list()
        folders = self.ctx.web.get_folder_by_server_relative_url(directory).folders.get().execute_query()

        for folder in folders:
            directory = folder.properties['ServerRelativeUrl']
            files = self.get_measures_files_obj(directory)
            contents.extend(files)

        contents.extend(folders)
        files = self.ctx.web.get_folder_by_server_relative_url(directory).files.get().execute_query()
        contents.extend(files)

        # filter out non files
        return list(filter(lambda content: content.entity_type_name == 'SP.File', contents))

    def download_file(self, file_obj, location):
        Path(location).mkdir(parents=True, exist_ok=True)
        filename = file_obj.name
        with open(f"{location}/{filename}", 'wb') as local_file:
            server_relative_url = file_obj.serverRelativeUrl
            print("Sharepoint downloading ", server_relative_url)
            self.ctx.web.get_file_by_server_relative_url(server_relative_url).download(local_file).execute_query()

    def download_measure_files_to_local_path(self, local_path):
        files = self.get_measures_files_obj()
        for file in files:
            self.download_file(file, local_path)
