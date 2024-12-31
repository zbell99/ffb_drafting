import pandas as pd

def fill_missing_columns(df, obj):
    '''
    Fills in missing columns with 0s
    '''
    for col, val in obj.__dict__.items():
        if col not in df.columns:
            df[col] = 0
    return df


def standardize_column_types(df, to_exclude):
    '''
    Standardizes the column types to float
    '''
    cols = [col for col in df.columns if col not in to_exclude]
    for col in cols:
        df[col] = df[col].astype(str)
        df[col] = pd.to_numeric(df[col].str.replace(',', ''))
        df[col] = df[col].astype(int)
    return df