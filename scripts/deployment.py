import json
import os
import shutil

from scripts.utils import get_latest_file


def store_production_files(dst: str, *args) -> None:
    """
    Copy files from their source directories to a destination dir

    :param dst: Destination dir to copy files
    :param args: Files to be be copied
    :return: None
    """
    os.makedirs(dst, exist_ok=True)
    for f in args:
        filename = f.split('\\')[1]
        new_filename = filename.split('_')[0] + '.' + filename.split('.')[-1]
        path = os.path.join(dst, new_filename)
        print(f'Copying {f} to {path}')
        shutil.copy2(f, path)


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    model_dir = config['output_model_path']
    output_folder_path = config['output_folder_path']
    deployment_path = config['prod_deployment_path']

    model_path = get_latest_file(model_dir, 'trainedmodel_*.pkl')
    metric_path = get_latest_file(model_dir, "latestscore_*.txt")
    ingest_record_path = get_latest_file(output_folder_path, "ingestedfiles_*.txt")

    store_production_files(deployment_path, model_path, metric_path, ingest_record_path)


if __name__ == '__main__':
    main()
