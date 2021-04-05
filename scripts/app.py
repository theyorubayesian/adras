import json
import os

import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask import request

import scripts.scoring as scorer
from scripts.diagnostics import check_execution_time
from scripts.diagnostics import check_missing_values
from scripts.diagnostics import dataframe_summary
from scripts.diagnostics import get_outdated_packages_list
from scripts.diagnostics import model_predictions
from scripts.training import prepare_dataset
from scripts.utils import load_model

load_dotenv(verbose=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/predict", methods=['POST', 'OPTIONS'])
def predict():
    data_json = request.get_json()
    df = pd.DataFrame(data_json['data'])
    print(df)
    predictions = model_predictions(df, model=prediction_model)
    print(predictions)
    return jsonify(predictions=predictions), 200


@app.route("/score", methods=['GET', 'OPTIONS'])
def score():
    return jsonify(score=scorer.main()), 200


@app.route("/summarise", methods=['GET', 'OPTIONS'])
def stats():
    return jsonify(summary=dataframe_summary(data)), 200


@app.route("/diagnose", methods=['GET', 'OPTIONS'])
def diagnose():
    missing_values = check_missing_values(data)
    execution_time = check_execution_time(
        training_script_output_dir=model_dir, ingestion_script_output_dir=dataset_csv_path
    )
    outdated_dependencies = get_outdated_packages_list(deployment_path)
    return jsonify(
        missing_values=missing_values,
        execution_time=execution_time,
        outdated_dependencies=outdated_dependencies
    ), 200


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    dataset_csv_path = config['output_folder_path']
    deployment_path = config['prod_deployment_path']
    model_dir = config['output_model_path']

    data = prepare_dataset(
        dataset_csv_path,
        dropped_columns=['corporation'],
        create_val_data=False
    )
    prediction_model = load_model(deployment_path, is_deployed=True)

    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, extra_files=['config.json'])
