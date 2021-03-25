import glob
import json
import os
import time

import pandas as pd
from pandas import DataFrame


def merge_multiple_dataframe(input_dir: str, output_dir: str) -> DataFrame:
    """
    Reads multiple CSV files into a pandas dataframe.

    :param input_dir: path to directory containing CSV files
    :param output_dir: list of ingested files are written to {output_dir}/ingestedfiles_*.txt
    :return: DataFrame containing all CSV datasets found in path
    """

    datasets = glob.glob(f'{input_dir}/*.csv')
    print(f"Found {len(datasets)} files. Creating dataframe")

    df = pd.concat(map(pd.read_csv, datasets))

    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/ingestedfiles_{time.strftime('%d%m%y%H%M%S')}.txt"
    with open(output_path, "w") as f:
        print(f"Writing list of ingested files to {output_path}")
        f.write("\n".join(datasets))

    return df


def clean_dataset(df: DataFrame) -> DataFrame:
    """
    All cleaning operations are done here.
    - Remove duplicate rows

    :param df: Input DataFrame to be cleaned
    :return: Cleaned DataFrame
    """
    temp = df.copy(deep=True)
    print(f"Input DataFrame is of shape: {temp.shape}")
    print("Missing Values", temp.isna().sum(), sep="\n")

    # Drop duplicate columns
    temp.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    print(f"Dropped duplicate rows. DataFrame is of shape: {temp.shape}")
    return temp


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    input_folder_path = config['input_folder_path']
    output_folder_path = config['output_folder_path']

    concat_df = merge_multiple_dataframe(input_folder_path, output_folder_path)
    cleaned_df = clean_dataset(concat_df)

    output_df_path = f"{output_folder_path}/finaldata_{time.strftime('%d%m%y%H%M%S')}.csv"
    print(f"Writing cleaned DataFrame to {output_df_path}")
    cleaned_df.to_csv(output_df_path, index=False)


if __name__ == '__main__':
    main()
