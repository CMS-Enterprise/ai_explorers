###################################################
# model_dataset
# loads modeling dataset
###################################################
import pandas as pd


def load_dataframe(path, drop_cols, keep_lag1=False):
    df = pd.read_csv(path)

    if drop_cols is not None and len(drop_cols) > 0:
        df = df.drop(columns=drop_cols)

    if not keep_lag1 and 'lag1' in df.columns:
        df = df.loc[df['lag1'].notna()].dropna(how="all")

    return df
