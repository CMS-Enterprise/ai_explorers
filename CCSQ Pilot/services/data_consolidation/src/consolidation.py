import os
from pathlib import Path

from .utils import get_measure_dir, get_config_settings, get_consolidated_dir
import pandas as pd


class Consolidation:
    def __init__(self):
        pd.set_option('display.max_columns', None)
        self.df = pd.DataFrame()

        settings = get_config_settings()

        self.provider_id_column_name = settings.get('provider_id_column_name')
        if self.provider_id_column_name is None:
            raise Exception("could not find provider_id_column_name")

        self.measure_id_column_name = settings.get('measure_id_column_name')
        if self.measure_id_column_name is None:
            raise Exception("could not find measure_id_column_name")

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.measure_start_date_column_name = settings.get('measure_start_date_column_name')
        if self.measure_start_date_column_name is None:
            raise Exception("could not find measure_start_date_column_name")

        self.measure_end_date_column_name = settings.get('measure_end_date_column_name')
        if self.measure_end_date_column_name is None:
            raise Exception("could not find measure_end_date_column_name")

    def load_all_measure_files(self):
        settings = get_config_settings()

        measure_dir = get_measure_dir()
        files = os.listdir(measure_dir)
        files = list(filter(lambda file: '.csv' in file, files))

        limiter = settings.get('limiter')
        if limiter is not None and 0 < limiter < len(files):
            print(f"limiter is set for loading measure files; loading {limiter} instead of {len(files)}")
            files = files[:limiter]

        dfs = []
        for filename in files:
            path = f"{measure_dir}/{filename}"
            print(f'Loading {filename}')
            df = pd.read_csv(path)
            # print(df.columns)
            dfs.append(df)

        if not len(dfs):
            raise Exception('Empty DataFrame, no csvs loaded')

        self.df = pd.concat(dfs)

    def load_local_df(self, path):
        self.df = pd.read_csv(path)

    def save_df_locally(self):
        settings = get_config_settings()

        local_temp_dir = get_consolidated_dir()
        Path(local_temp_dir).mkdir(parents=True, exist_ok=True)

        measure_specific_filename = settings.get('MEASURE_SPECIFIC_FILENAME')
        path = f"{local_temp_dir}/{measure_specific_filename}"
        self.df.to_csv(path, index=False)

    def normalize_column_variations(self):
        settings = get_config_settings()

        column_variations = settings.get('column_variations', [])
        if column_variations is None or len(column_variations) == 0:
            print("column_variations is blank, skipping normalizing variations")
            return

        for column_variation in column_variations:
            print("Normalizing Column Variation ", column_variation)
            main = column_variation[0]

            if main not in self.df:
                self.df[main] = None

            for x in range(1, len(column_variation)):
                variation = column_variation[x]

                if variation in self.df:
                    self.df[main].fillna(self.df[variation], inplace=True)
                    del self.df[variation]

    def drop_unnamed_columns(self):
        print("Dropping Unnamed Columns")
        self.df = self.df.loc[:, ~self.df.columns.str.match("Unnamed")]

    def drop_nan_rows(self):
        settings = get_config_settings()

        drop_nan_rows_for_columns = settings.get('drop_nan_rows_for_columns', [])
        if drop_nan_rows_for_columns is None or len(drop_nan_rows_for_columns) == 0:
            print("drop_nan_rows_for_columns is blank, skipping dropping nan rows")
            return

        for col in drop_nan_rows_for_columns:
            print("Dropping NaN rows for columns", col)
            self.df = self.df[self.df[col].notna()]

    def filter_measure_id(self):
        settings = get_config_settings()

        filter_measure = settings.get('filter_measure')
        if filter_measure is None or len(filter_measure) == 0:
            print("filter_measure is blank, skipping filtering measure")
            return

        print("Filtering for measure id ", filter_measure)
        self.df = self.df[self.df[self.measure_id_column_name] == filter_measure]

    def normalize_provider_id(self):
        print("Normalizing Provider Ids")
        # convert to string first to get rid of quotes that are failing int conversion
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(str)
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].str.replace("'", "")
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].str.replace(".0", "", regex=False)

        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].str.strip("0")

        # # then float convert to get around .0s in strings; then finally to int
        # self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(float)
        # self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(int)

    def normalize_measure_id(self):
        print("Normalizing Measure Ids")
        self.df[self.measure_id_column_name] = self.df[self.measure_id_column_name].str.replace('-', '_')

    def normalize_score(self):
        print("Normalizing Scores")
        self.df[self.score_column_name] = pd.to_numeric(self.df[self.score_column_name], errors='coerce')
        self.df = self.df[self.df[self.score_column_name] > 0]

    def normalize_measure_start_date(self):
        print("Normalizing Measure Start Date")
        self.df[self.measure_start_date_column_name] = pd.to_datetime(
            self.df[self.measure_start_date_column_name], errors='coerce'
        )

    def normalize_measure_end_date(self):
        print("Normalizing Measure End Date")
        self.df[self.measure_end_date_column_name] = pd.to_datetime(
            self.df[self.measure_end_date_column_name], errors='coerce'
        )

    # TODO: How can this come from a config?
    def reorder_columns(self):
        col_order = [
            self.provider_id_column_name,
            self.score_column_name,
            # self.measure_id_column_name,
            # self.measure_start_date_column_name,
            self.measure_end_date_column_name,
        ]

        row_sort = [
            self.provider_id_column_name, self.measure_end_date_column_name
        ]

        self.df = self.df[col_order]
        self.df = self.df.drop_duplicates()
        self.df = self.df.sort_values(by=row_sort)
        self.df = self.df.reset_index(drop=True)

    def drop_duplicates(self):
        self.df = self.df.drop_duplicates()

    def consolidate(self):
        self.load_all_measure_files()
        self.drop_unnamed_columns()

        # print(self.df)

        self.normalize_column_variations()
        self.normalize_provider_id()
        self.normalize_measure_id()
        self.normalize_score()
        self.normalize_measure_start_date()
        self.normalize_measure_end_date()
        self.drop_nan_rows()

        self.filter_measure_id()
        self.reorder_columns()
        self.drop_duplicates()

        # self.df = self.df.loc[self.df[self.provider_id_column_name] == '10001']

        print(self.df.head(20))
