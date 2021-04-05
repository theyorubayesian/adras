import json
import os
import time

import pandas as pd
import requests

from scripts.scoring import prepare_data

URL = "http://127.0.0.1:8000/"


def main(output_dir: str = None):
    with open('config.json', 'r') as f:
        config = json.load(f)

    test_data_path = config['test_data_path']
    model_path = config['output_model_path']

    data = prepare_data(test_data_path, dropped_columns=["corporation"])
    input_data = data['test']['X'].to_json(orient='table', index=False)
    print(pd.DataFrame(json.loads(input_data)['data']))

    headers = {'Content-Type': 'application/json'}

    predictions = requests.post(URL + 'predict', input_data, headers=headers)
    print(predictions.json())

    score = requests.get(URL + 'score')
    print(score.json())

    summary = requests.get(URL + 'summarise')
    print(summary.json())

    diagnosis = requests.get(URL + 'diagnose')
    print(diagnosis.json())

    response = {
        'predictions': predictions.json(),
        'score': score.json(),
        'summary': summary.json(),
        'diagnosis': diagnosis.json()
    }

    output_dir = output_dir or model_path
    output_file = os.path.join(output_dir, f'apireturns_{time.strftime("%y%m%d%H%M%S")}.txt')
    with open(output_file, 'w') as f:
        print(f'Writing API reponses to {output_file}')
        f.write(json.dumps(response, indent=4))


if __name__ == '__main__':
    main()
