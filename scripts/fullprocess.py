import glob
import json
import os
from typing import Tuple

from scripts.deployment import main as deploy
from scripts.apicalls import main as make_api_calls
from scripts.ingestion import main as ingest
from scripts.reporting import main as report
from scripts.scoring import main as score
from scripts.training import main as train


def check_new_files(dataset_dir: str, ingestion_record: str) -> bool:
    """
    Check for files in dataset_dir not in ingestion_record
    :param dataset_dir: Directory containing CSV datasets
    :param ingestion_record: File containing list of already ingested datasets
    :return: True if new files exist in dataset_dir else False
    """
    print('Checking for new files...')
    with open(ingestion_record, 'r') as f:
        ingested_files = f.read().splitlines()

    candidate_files = glob.glob(f'{dataset_dir}/*.csv')
    new_files = [f for f in candidate_files if f not in ingested_files]
    return bool(new_files)


def check_model_drift(metric_file: str) -> Tuple[bool, float, float]:
    """
    Train and score new model on latest finaldata_*.csv.
    Compare new F1-Score to old one.
    :param metric_file: File containing old F1-Score
    :return: New F1-Score > Old F1-Score, new F1-Score, old F1-Score
    """
    print('Checking for model drift...')
    with open(metric_file, 'r') as f:
        old_f1_score = float(f.readline().strip())

    train()
    new_f1_score = score()

    return new_f1_score > old_f1_score, new_f1_score, old_f1_score


def main():
    print("Running fullprocess...")
    with open('config.json', 'r') as f:
        config = json.load(f)

    input_folder_path = config['input_folder_path']
    deployment_path = config['prod_deployment_path']
    model_path = config['output_model_path']

    ingestion_record = os.path.join(deployment_path, 'ingestedfiles.txt')
    if not check_new_files(input_folder_path, ingestion_record):
        print(f'No new dataset in {input_folder_path}. Ending process...')
        exit()

    ingest()

    metric_file = os.path.join(deployment_path, 'latestscore.txt')
    drift, new_score, old_score = check_model_drift(metric_file)
    if not drift:
        print('Production model performs better. '
              f'New F1-Score: {new_score}. Old F1-Score: {old_score}')
        exit()

    deploy()
    report()
    make_api_calls()


if __name__ == '__main__':
    main()
