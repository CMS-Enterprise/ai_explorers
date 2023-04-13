from .utils import get_tmp_dir, get_config_settings
import pandas as pd


class Engineering:
    def __init__(self):
        pd.set_option('display.max_columns', None)
        self.df = pd.DataFrame()

        settings = get_config_settings()

        self.provider_id_column_name = settings.get('provider_id_column_name')
        if self.provider_id_column_name is None:
            raise Exception("could not find provider_id_column_name")

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.measure_start_date_column_name = settings.get('measure_start_date_column_name')
        if self.measure_start_date_column_name is None:
            raise Exception("could not find measure_start_date_column_name")

        self.measure_end_date_column_name = settings.get('measure_end_date_column_name')
        if self.measure_end_date_column_name is None:
            raise Exception("could not find measure_end_date_column_name")

        self.y_quarter_column_name = settings.get('y_quarter_column_name')
        if self.y_quarter_column_name is None:
            raise Exception("could not find y_quarter_column_name")

        self.year_column_name = settings.get('year_column_name')
        if self.year_column_name is None:
            raise Exception("could not find year_column_name")

        self.quarter_column_name = settings.get('quarter_column_name')
        if self.quarter_column_name is None:
            raise Exception("could not find quarter_column_name")

        self.backfill_lag = settings.get('backfill_lag')
        self.backfill_prov_mean = settings.get('backfill_prov_mean')

    def load_dataframe(self):
        settings = get_config_settings()

        tmp_dir = get_tmp_dir()
        filename = settings.get('MEASURE_SPECIFIC_FILENAME')
        path = f'{tmp_dir}/{filename}'

        self.df = pd.read_csv(path)
        if self.df is None:
            raise Exception('Could not load in csv')

    def save_df_as_csv(self, path):
        self.df.to_csv(path, index=False)

    def save_df_locally(self):
        settings = get_config_settings()

        tmp_dir = get_tmp_dir()
        filename = settings.get('MEASURE_SPECIFIC_FILENAME')
        path = f'{tmp_dir}/{filename}'

        self.save_df_as_csv(path)

    # TODO: How can this come from a config?
    def drop_measure_dates(self):
        self.df = self.df.drop(columns=[self.measure_end_date_column_name])

    def add_y_quarters(self):
        self.df[self.y_quarter_column_name] = self.df[self.measure_end_date_column_name].dt.to_period('Q')

    def sort_by_prov_and_y_quarter(self):
        row_sort = [
            self.provider_id_column_name, self.y_quarter_column_name
        ]

        self.df = self.df.sort_values(by=row_sort)
        self.df = self.df.reset_index(drop=True)

    def turn_y_quarter_to_year_quarter(self):
        self.df[self.year_column_name] = self.df[self.y_quarter_column_name].apply(lambda x: x.year)
        self.df[self.quarter_column_name] = self.df[self.y_quarter_column_name].apply(lambda x: x.quarter)
        del self.df[self.y_quarter_column_name]

    def add_lags(self):
        settings = get_config_settings()

        lag_to_add = settings.get('lag_to_add')
        if lag_to_add is None or lag_to_add == 0:
            print("lag_to_add is blank, skipping lags")
            return

        for i in range(1, lag_to_add + 1):
            lag_column_name = f"lag{i}"
            print("Adding ", lag_column_name)
            self.df[lag_column_name] = self.df.groupby([self.provider_id_column_name])[self.score_column_name].shift(i)

    def fill_lags(self):
        settings = get_config_settings()

        lag_to_add = settings.get('lag_to_add')
        if lag_to_add is None or lag_to_add == 0:
            print("lag_to_add is blank, nothing to fill")
            return

        if not self.backfill_lag:
            print("backfill_lag is false, skipping fill")
            return

        lag_fill_df = self.df.copy().filter(items=[self.provider_id_column_name, 'lag1'])
        lag_fill_df.dropna()
        lag_fill_df = lag_fill_df \
            .groupby(self.provider_id_column_name) \
            .first() \
            .reset_index() \
            .rename(columns={'lag1': 'lag_filler'})

        self.df = self.df.merge(
            lag_fill_df,
            how='left',
            on=self.provider_id_column_name)

        for i in range(1, lag_to_add + 1):
            lag_column_name = f"lag{i}"
            print("Lag filling  ", lag_column_name)
            self.df[lag_column_name] = self.df[lag_column_name].fillna(self.df['lag_filler']).fillna(
                self.df[self.score_column_name])

        self.df = self.df.drop(columns=['lag_filler'])

    def fill_prov_mean(self):
        if not self.backfill_prov_mean:
            print("backfill_prov_mean is false, skipping fill")
            return

        settings = get_config_settings()

        prov_mean_diff = settings.get('prov_mean_diff_column_name')
        if prov_mean_diff is None or len(prov_mean_diff) == 0:
            print("prov_mean_diff_column_name is blank, skipping add prov mean diff")
            return

        prov_mean_column_name = settings.get('prov_mean_column_name')
        if prov_mean_column_name is None or len(prov_mean_column_name) == 0:
            print("prov_mean_column_name is blank, skipping add prov mean diff")
            return

        # def add_prov_mean_diff(self):
        # self.df[prov_mean_diff] = self.df[self.score_column_name] - self.df[prov_mean_column_name]

        fill_df = self.df.copy().filter(items=[self.provider_id_column_name, prov_mean_column_name])
        fill_df.dropna()
        fill_df = fill_df \
            .groupby(self.provider_id_column_name) \
            .first() \
            .reset_index() \
            .rename(columns={prov_mean_column_name: 'filler'})

        self.df = self.df.merge(
            fill_df,
            how='left',
            on=self.provider_id_column_name)

        print('Prov mean filling')
        self.df[prov_mean_column_name] = self.df[prov_mean_column_name].fillna(self.df['filler']).fillna(
            self.df[self.score_column_name])

        self.df = self.df.drop(columns=['filler'])

    def add_lag_diff(self):
        settings = get_config_settings()

        lag_to_add = settings.get('lag_to_add')
        if lag_to_add is None or lag_to_add == 0:
            print("lag_to_add is blank, skipping add lag diff")
            return

        lag_diff_column_name = settings.get('lag_diff_column_name')
        if lag_diff_column_name is None or len(lag_diff_column_name) == 0:
            print("lag_diff_column_name is blank, skipping add lag diff")
            return

        self.df[lag_diff_column_name] = self.df[self.score_column_name] - self.df.lag1

    def add_prov_mean_diff(self):
        settings = get_config_settings()

        prov_mean_diff = settings.get('prov_mean_diff_column_name')
        if prov_mean_diff is None or len(prov_mean_diff) == 0:
            print("prov_mean_diff_column_name is blank, skipping add prov mean diff")
            return

        prov_mean_column_name = settings.get('prov_mean_column_name')
        if prov_mean_column_name is None or len(prov_mean_column_name) == 0:
            print("prov_mean_column_name is blank, skipping add prov mean diff")
            return

        self.df[prov_mean_diff] = self.df[self.score_column_name] - self.df[prov_mean_column_name]

    def add_provider_mean(self):
        settings = get_config_settings()

        prov_mean_column_name = settings.get('prov_mean_column_name')
        if prov_mean_column_name is None or len(prov_mean_column_name) == 0:
            print("prov_mean_column_name is blank, skipping add prov mean")
            return

        cumm_mean_func = (lambda x: x.shift(1).expanding().mean())
        self.df[prov_mean_column_name] = \
            self.df.groupby(self.provider_id_column_name, group_keys=False)[self.score_column_name].apply(
                cumm_mean_func)

    def drop_duplicates(self):
        self.df = self.df.drop_duplicates(subset=['provider_id', 'measure_end_date'], keep='last').drop_duplicates()

    def normalize_provider_id(self):
        print("Normalizing Provider Ids")
        # convert to string first to get rid of quotes that are failing int conversion
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(str)
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].str.replace("'", "")
        self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].str.replace(".0", "", regex=False)

        # then float convert to get around .0s in strings; then finally to int
        # self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(float)
        # self.df[self.provider_id_column_name] = self.df[self.provider_id_column_name].astype(int)

    def normalize_score(self):
        print("Normalizing Scores")
        self.df[self.score_column_name] = pd.to_numeric(self.df[self.score_column_name], errors='coerce')
        self.df = self.df[self.df[self.score_column_name] > 0]

    # def normalize_measure_start_date(self):
    #     print("Normalizing Measure Start Date")
    #     self.df[self.measure_start_date_column_name] = pd.to_datetime(
    #         self.df[self.measure_start_date_column_name], errors='coerce'
    #     )

    def normalize_measure_end_date(self):
        print("Normalizing Measure End Date")
        self.df[self.measure_end_date_column_name] = pd.to_datetime(
            self.df[self.measure_end_date_column_name], errors='coerce'
        )

    def drop_nan_rows(self):
        settings = get_config_settings()

        drop_nan_rows_for_columns = settings.get('drop_nan_rows_for_columns', [])
        if drop_nan_rows_for_columns is None or len(drop_nan_rows_for_columns) == 0:
            print("drop_nan_rows_for_columns is blank, skipping dropping nan rows")
            return

        for col in drop_nan_rows_for_columns:
            print("Dropping NaN rows for columns", col)
            self.df = self.df[self.df[col].notna()]

    def renormalize(self):
        """
        csv's lose data types, so re-normalize everything

        :return:
        """
        self.normalize_provider_id()
        self.normalize_score()
        # self.normalize_measure_start_date()
        self.normalize_measure_end_date()
        self.drop_nan_rows()
        self.drop_duplicates()

    def add_features(self):
        self.add_y_quarters()
        self.sort_by_prov_and_y_quarter()
        self.add_lags()
        self.fill_lags()
        self.turn_y_quarter_to_year_quarter()
        self.add_lag_diff()
        self.add_provider_mean()
        self.fill_prov_mean()
        self.add_prov_mean_diff()

    def run(self):
        self.load_dataframe()
        self.renormalize()
        self.add_features()
        self.drop_measure_dates()

        print(self.df.head(20))
        return self.df
