from pathlib import Path

from .utils import get_config_settings, get_tmp_dir


class Metadata:
    def __init__(self, df):
        settings = get_config_settings()

        self.df = df

        full_measure_s3_prefix = settings.get('FULL_MEASURE_S3_PREFIX')
        self.log = f"Modeling Dataset Metadata for {full_measure_s3_prefix}\n\n"

        self.year_column_name = settings.get('year_column_name')
        if self.year_column_name is None:
            raise Exception("could not find year_column_name")

        self.quarter_column_name = settings.get('quarter_column_name')
        if self.quarter_column_name is None:
            raise Exception("could not find quarter_column_name")

        self.provider_id_column_name = settings.get('provider_id_column_name')
        if self.provider_id_column_name is None:
            raise Exception("could not find provider_id_column_name")

    def add_column_name_and_data_type(self):
        self.log += "Columns/Data Types\n"

        for col in self.df.columns:
            self.log += f"\t{col}:\t{self.df[col].dtypes}\n"

    def pad_log(self):
        self.log += "\n"

    def add_earliest_latest_dates(self):
        self.df['tmp_y_quarter'] = \
            self.df[self.year_column_name].astype(str) + 'Q' + self.df[self.quarter_column_name].astype(str)

        earliest_quarter = self.df['tmp_y_quarter'].min()
        latest_quarter = self.df['tmp_y_quarter'].max()

        self.log += f"Earliest Measure Quarter: {earliest_quarter}\n"
        self.log += f"Latest Measure Quarter: {latest_quarter}\n"

        del self.df['tmp_y_quarter']

    def add_dimensions(self):
        self.log += f"Dataset Dimensions: {self.df.shape}\n"

    def add_provider_count(self):
        self.log += f"Unique Provider Count: {self.df[self.provider_id_column_name].unique().size}\n"

    def write_log_locally(self):
        settings = get_config_settings()

        local_temp_dir = get_tmp_dir()
        Path(local_temp_dir).mkdir(parents=True, exist_ok=True)

        measure_specific_filename = settings.get('MEASURE_SPECIFIC_FILENAME')
        consolidated_metadata_file_prefix = settings.get('feature_engineered_metadata_file_prefix')

        path = f"{local_temp_dir}/{consolidated_metadata_file_prefix}{measure_specific_filename}" \
            .replace('.csv', '.txt')
        with open(path, "w") as f:
            print('Saving Metadata logs to ', path)
            f.write(self.log)

    def generate(self):
        self.add_column_name_and_data_type()
        self.pad_log()
        self.add_earliest_latest_dates()
        self.pad_log()
        self.add_dimensions()
        self.pad_log()
        self.add_provider_count()
