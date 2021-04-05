import json
import os

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

from scripts.diagnostics import model_predictions
from scripts.scoring import prepare_data


def score_model(data: dict, model_dir: str, labels: list = None, output_dir: str = None) -> None:
    """
    Makes predictions on test data and saves Confusion Matrix to output_dir
    :param data: Dataset to be predicted upon.
                Should have form:{'test': {'X': <Xdf>, 'y': <y_df>}}
    :param model_dir: Path to dir containing model
    :param labels: Labels for Confusion Matrix
    :param output_dir: Directory where Confusion Matrix plot is saved to
    :return: None
    """
    X = data['test']['X']
    predictions = model_predictions(X, model_path=model_dir)
    cm = confusion_matrix(data['test']['y'], predictions)
    print('Confusion Matrix', cm, sep='\n')

    cm_display = ConfusionMatrixDisplay(cm, display_labels=labels)
    cm_display.plot()

    img_path = os.path.join(output_dir, "confusion_matrix.png")
    print(f"Saving Confusion Matrix image to {img_path}")
    plt.savefig(img_path)


def main(model_dir: str = None, output_dir: str = None):
    with open('config.json', 'r') as f:
        config = json.load(f)

    deployment_path = config['prod_deployment_path']
    model_path = config['output_model_path']
    test_data_path = config['test_data_path']

    data = prepare_data(test_data_path, dropped_columns=["corporation"])
    model_dir = model_dir or deployment_path
    output_dir = output_dir or model_path
    score_model(
        data, model_dir=model_dir, labels=['not exited', 'exited'], output_dir=output_dir
    )


if __name__ == '__main__':
    main()
