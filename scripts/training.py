import glob
import json
import os
import pickle
import time
from typing import Union

import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split


def prepare_dataset(
        dataset_path: str,
        val_size: float = 0.1,
        create_val_data: bool = True,
        dropped_columns: list = None
) -> Union[dict, DataFrame]:
    """
    Reads the most recent dataset 'finaldata_*.csv' from
    the dataset_path and prepares it for training

    :param dataset_path: Directory containing CSV datasets named 'finaldata_*.csv'
    :param val_size: test_size to use in train_test_split when creating validation data
    :param create_val_data:
    :param dropped_columns: Columns to drop from dataset
    :return:
    if create_val_data:
        {
            'training: {'X': <x_train_df>: 'y': <y_train_df>},
            'val': {'X': <x_val_df', 'y': <y_val_df>}
        }
    else DataFrame
    """
    dataset_list = glob.glob(f"{dataset_path}/finaldata_*.csv")
    dataset_list.sort()
    dataset = pd.read_csv(dataset_list[-1])     # Most recent dataset is used.
    print(f"DataFrame was successfully created from {dataset_list[-1]}")
    dataset.drop(dropped_columns, axis=1, inplace=True)
    print(f"Dropped columns: {dropped_columns}")

    if create_val_data:
        x_train, x_val = train_test_split(dataset, test_size=val_size, random_state=42)
        y_train, y_val = x_train.pop("exited"), x_val.pop("exited")
        data = {"training": {"X": x_train, "y": y_train}, "val": {"X": x_val, "y": y_val}}
        print(f"{val_size*100}% of dataset is held out as validation data")
        return data
    return dataset


def train_model(data: dict, model_dir: str) -> None:
    """
    Fits model on input data, calculates performance metrics and
    dumps model to dir
    :param data: Data dictionary containing
    :param model_dir: Path to dir containing model
    :return: None
    """
    model = LogisticRegression(
        C=1.0,
        class_weight=None,
        dual=False,
        fit_intercept=True,
        intercept_scaling=1,
        l1_ratio=None,
        max_iter=100,
        multi_class='auto',
        n_jobs=None,
        penalty='l2',
        tol=0.0001,
        verbose=0,
        warm_start=False
    )
    print("Fitting model...")
    model.fit(data["training"]["X"], data["training"]["y"])

    accuracy = model.score(data["val"]["X"], data["val"]["y"])
    print(f"Model Accuracy: {accuracy}")

    predictions = model.predict(data["val"]["X"])
    f1score = f1_score(data["val"]["y"], predictions)
    print(f"Model F1-Score: {f1score}")

    print(classification_report(data["val"]["y"], predictions))

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"trainedmodel_{time.strftime('%y%m%d%H%M%S')}.pkl")
    print(f"Persisting fitted model to {model_path}...")
    with open(model_path, "wb") as modelfile:
        pickle.dump(model, modelfile)


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    dataset_csv_path = config['output_folder_path']
    model_dir = config['output_model_path']
    dropped_columns = ["corporation"]
    val_size = 0.1

    data = prepare_dataset(
        dataset_csv_path,
        dropped_columns=dropped_columns,
        val_size=val_size,
        create_val_data=True
    )
    train_model(data, model_dir=model_dir)


if __name__ == '__main__':
    main()
