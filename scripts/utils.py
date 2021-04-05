import glob
import os
import pickle
from typing import Optional

from sklearn.linear_model import LogisticRegression


def get_latest_file(path: str, filename: str) -> str:
    """
    Returns the most recent version of a file by sorting files lexicographically.
    Files should have datetime in their filename

    :param path: Directory containing files
    :param filename: Filename f-strings to be passed into glob.glob
    :return: Most lexicographically great file found
    """
    latest_file = ''
    filepath = os.path.join(path, filename)
    files = glob.glob(filepath)
    files.sort()
    print(f"Searching for {filepath}. Found {len(files)} files.")

    if files:
        latest_file = files[-1]
        print(f"Latest file is {files[-1]}")
    return latest_file


def load_model(model_path: str, is_deployed: bool = False) -> Optional[LogisticRegression]:
    """
    Load model from pkl file in model_path
    :param model_path: Directory containing model pkl file
    :param is_deployed: Model being loaded is in production.
    Filenames are different in development and production
    :return: Fitted Logistic Regression model or
    None if trainedmodel.pkl not found in model_path
    """
    latest_model = os.path.join(model_path, 'trainedmodel.pkl') if is_deployed \
        else get_latest_file(model_path, 'trainedmodel_*.pkl')

    if latest_model:
        model = pickle.load(open(latest_model, 'rb'))
        return model
    return None
