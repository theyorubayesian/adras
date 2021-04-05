import os
import json
import subprocess
import time
import timeit

from pandas import DataFrame
from sklearn.linear_model import LogisticRegression

from scripts.training import prepare_dataset
from scripts.utils import load_model


def model_predictions(data: DataFrame, model_path: str = None, model: LogisticRegression = None) -> list:
    """
    Make predictions on input data using model found in model_path
    :param data: Data for which predictions are to be made
    :param model_path: Directory containing model pkl file
    :param model: Fitted model. Is used if passed else model is loaded from model_path
    :return: List of model predictions
    """
    assert any([model, model_path]), "model or model_path must be passed into function"
    if not model:
        model = load_model(model_path, is_deployed=True)

    predictions = model.predict(data)
    return [float(x) for x in list(predictions)]


def check_missing_values(data: DataFrame) -> DataFrame:
    """
    Checks % of missing values per column in data
    :param data: DataFrame to be checked for NA
    :return: List of missing values percentages in DataFrame columns
    """
    missing_values_df = data.isna().sum() / data.shape[0]
    print(missing_values_df)
    return missing_values_df.values.tolist()


def dataframe_summary(data: DataFrame) -> list:
    """
    Summary statistics calculated are:
        - Mean
        - Median
        - Standard Deviation
    :param data: DataFrame to be summarised.
    :return: summary_dataframe.values.tolist()
    """
    statistics = data.agg(["mean", "median", "std"])
    return statistics.values.tolist()


def clean_up_diagnostic_files(start_time: str, end_time: str, folder: str) -> None:
    for f in os.listdir(folder):
        if f'_{time.strftime("%y")}' not in f:
            continue
        creation_time = f.split('_')[1].split('.')[0]
        if start_time <= creation_time <= end_time:
            os.remove(os.path.join(folder, f))


def check_execution_time(
        training_script_output_dir: str,
        ingestion_script_output_dir: str,
        n_executions: int = 1000
) -> list:
    """
    Calculates execution time for the ingestion and training script.
    :param training_script_output_dir:
    :param ingestion_script_output_dir:
    :param n_executions: Number of executions to average from. Default is 1000.
    :return: [training_script_time, ingestion_script_time]
    """
    print("Timing the training script...")
    start_time = time.strftime('%y%m%d%H%M%S')
    training_script_time = timeit.timeit(
        stmt="main()", setup="from scripts.training import main", number=n_executions
    )
    end_time = time.strftime('%y%m%d%H%M%S')
    print(f"Training script takes {training_script_time}s")
    clean_up_diagnostic_files(start_time, end_time, training_script_output_dir)

    print("Timing the ingestion script...")
    start_time = time.strftime('%y%m%d%H%M%S')
    ingestion_script_time = timeit.timeit(
        stmt="main()", setup="from scripts.ingestion import main", number=n_executions
    )
    end_time = time.strftime('%y%m%d%H%M%S')
    print(f"Ingestion script takes {ingestion_script_time}s")
    clean_up_diagnostic_files(start_time, end_time, ingestion_script_output_dir)
    return [training_script_time, ingestion_script_time]


def get_outdated_packages_list(output_dir: str) -> str:
    """
    Check the environment for outdated packages.
    Uses 'pip list --outdated --format columns'.
    :param output_dir: List is written to output_dir.
    :return: None
    """
    print("Checking for outdated packages...")
    process = subprocess.run(
        "pip list --outdated --format columns",
        shell=True,
        capture_output=True,
        check=True,
        text=True
    )
    output = process.stdout
    print(output)

    outdated_packages_file = os.path.join(
        output_dir, "outdated_packages.txt"
    )
    with open(outdated_packages_file, 'w') as f:
        print(f"Writing list of outdated packages to {outdated_packages_file}")
        f.write(process.stdout)
    return process.stdout


def main():
    with open("config.json", 'r') as f:
        config = json.load(f)

    dataset_csv_path = config['output_folder_path']
    deployment_path = config['prod_deployment_path']
    model_dir = config['output_model_path']
    output_folder_path = config['output_folder_path']

    data = prepare_dataset(
        dataset_csv_path,
        dropped_columns=["corporation"],
        create_val_data=False
    )

    dataframe_summary(data)
    check_missing_values(data)
    model_predictions(data.drop("exited", axis=1), model_path=deployment_path)
    check_execution_time(
        training_script_output_dir=model_dir, ingestion_script_output_dir=output_folder_path
    )
    # TODO: Should diagnostics be written to deployment path?
    get_outdated_packages_list(deployment_path)


if __name__ == '__main__':
    main()
