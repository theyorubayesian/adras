import os
import glob
import json
import time

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score

from scripts.utils import get_latest_file
from scripts.utils import load_model


def prepare_data(dataset_path: str, dropped_columns: list = None) -> dict:
    """
    Prepares test dataset for use.
    :param dataset_path: Directory contained CSV dataset(s)
    :param dropped_columns: List of columns to be dropped from DataFrame
    :return:
    """
    dataset_list = glob.glob(f"{dataset_path}/*.csv")
    print(f"Found {len(dataset_list)} files. Creating dataframe")

    df = pd.concat(map(pd.read_csv, dataset_list))
    if dropped_columns:
        df.drop(dropped_columns, axis=1, inplace=True)
    print(f"Test dataset is of shape: {df.shape}")

    y = df.pop("exited")
    data = {"test": {"X": df, "y": y}}
    return data


def score_model(
        data: dict,
        model: LogisticRegression,
        output_to_file: bool = True,
        metric_output_dir: str = None
) -> float:
    """
    Use input model to make predictions on test data and calculate F1-Score
    :param data: Data for which predictions are to be mad.e
    :param model: Trained LogisticRegression model
    :param output_to_file: Whether to write F1-Score to file
    :param metric_output_dir: Directory where F1-Score is written to
    :return: None
    """
    predictions = model.predict(data["test"]["X"])
    print(classification_report(data["test"]["y"], predictions))

    f1score = f1_score(data["test"]["y"], predictions)
    print(f"Model F1-Score: {f1score}")

    if output_to_file:
        if not metric_output_dir:
            raise Exception("metric_output_dir should not be None")
        os.makedirs(metric_output_dir, exist_ok=True)
        metric_file_path = os.path.join(
            metric_output_dir, f"latestscore_{time.strftime('%y%m%d%H%M%S')}.txt"
        )
        with open(metric_file_path, "w") as f:
            print(f"Writing F1-Score to {metric_file_path}")
            f.write(str(f1score))
    return f1score


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    model_path = config['output_model_path']
    test_data_path = config['test_data_path']

    data = prepare_data(test_data_path, dropped_columns=["corporation"])
    model = load_model(model_path)

    if model is None:
        raise Exception(f"No model found in {model_path}")

    return score_model(data, model, metric_output_dir=model_path)


if __name__ == '__main__':
    main()
