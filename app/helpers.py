import pandas as pd
from fuzzywuzzy import process

def fill_missing_columns(df, obj):
    '''
    Fills in missing columns with 0s
    '''
    for col in obj:
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


def fuzzy_match(item, names, matches = {}, score=95):
    '''
    Pairs an item to its closest match in a list of names. If the match score is above a certain threshold, it is stored in a dictionary.
    '''
    match = process.extractOne(item, names)
    # print(matches)
    # print(item, match[0], match[1])
    if match[1] >= score:
        matches[item] = match[0]
    # print(matches)
    return matches