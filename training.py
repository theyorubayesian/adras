from flask import Flask, session, jsonify, request
import pandas as pd
import numpy as np
import pickle
import os
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import json

from pandas import DataFrame


def train_model(data: DataFrame) -> LogisticRegression:
    model = LogisticRegression(
        C=1.0,
        class_weight=None,
        dual=False,
        fit_intercept=True,
        intercept_scaling=1,
        l1_ratio=None,
        max_iter=100,
        multi_class='warn',
        n_jobs=None,
        penalty='l2',
        tol=0.0001,
        verbose=0,
        warm_start=False
    )
    
    #fit the logistic regression to your data
    
    #write the trained model to your workspace in a file called trainedmodel.pkl
    return model


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    dataset_csv_path = config['output_folder_path']
    model_path = config['output_model_path']

    data = pd.read_csv(dataset_csv_path)
    train, test = train_test_split(data, test_size=)


if __name__ == '__main__':
    main()