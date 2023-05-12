# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Predict distance of geo-referenced centroid
# Author: Amanda Droghini (adroghini@alaska.edu)
# Usage: Must be executed in a Python 3.9 installation.
# Description: This script uses leave-one-out cross validation and a linear regression model to predict distance of geo-referenced centroids from height and speed of the aircraft.
# ---------------------------------------------------------------------------

# Import packages
import time
import datetime
from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
import os

# Set root directory
drive = 'D:\\'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
imagery_folder = os.path.join(project_folder, 'Data_Input/imagery/aerial')

# Define inputs
input_csv = os.path.join(imagery_folder, 'AerialImagery_Metadata_Subset.csv')

# Read in data
model_data = pd.read_csv(input_csv)

# Define variable sets
predictor_all = ['height', 'speed']
response = ['Shape_Length']
all_variables = predictor_all + response
outer_cv_split_n = ['outer_cv_split_n']
prediction = ['prediction']
output_variables = all_variables + outer_cv_split_n + prediction

# Create an empty data frame to store the outer cross validation splits
outer_train = pd.DataFrame(columns=all_variables)
outer_test = pd.DataFrame(columns=all_variables)

# Create an empty data frame to store the outer test results
outer_results = pd.DataFrame(columns=output_variables)

# Define cross validation
outer_cv_splits = LeaveOneOut()

# Create outer cross validation splits
count = 1
for train_index, test_index in outer_cv_splits.split(model_data,
                                                     model_data[response[0]]):
    # Split the data into train and test partitions
    train = model_data.iloc[train_index]
    test = model_data.iloc[test_index]
    # Insert outer_cv_split_n to train
    train = train.assign(outer_cv_split_n=count)
    # Insert iteration to test
    test = test.assign(outer_cv_split_n=count)
    # Append to data frames
    outer_train = outer_train.append(train, ignore_index=True, sort=True)
    outer_test = outer_test.append(test, ignore_index=True, sort=True)
    # Increase counter
    count += 1
cv_length = count - 1
print(f'\tCreated {cv_length} outer cross-validation group splits.')

# Reset indices
outer_train = outer_train.reset_index()
outer_test = outer_test.reset_index()

# Iterate through outer cross validation splits
outer_cv_i = 1
while outer_cv_i <= cv_length:
    #### CONDUCT MODEL TRAIN
    ####____________________________________________________

    # Partition the outer train split by iteration number
    print(f'\tConducting outer cross-validation iteration {outer_cv_i} of {cv_length}...')
    train_iteration = outer_train[outer_train['outer_cv_split_n'] == outer_cv_i].copy()

    # Identify X and y train splits
    X_train = train_iteration[predictor_all].astype(float).copy()
    y_train = train_iteration[response[0]].astype(float).copy()

    # Train model
    print('\t\tTraining model...')
    iteration_start = time.time()
    outer_model = LinearRegression()
    outer_model.fit(X_train, y_train)
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    #### CONDUCT MODEL TEST
    ####____________________________________________________

    # Partition the outer test split by iteration number
    print('\t\tPredicting outer cross-validation test data...')
    iteration_start = time.time()
    test_iteration = outer_test[outer_test['outer_cv_split_n'] == outer_cv_i].copy()

    # Identify X test split
    X_test = test_iteration[predictor_all]

    # Use the model to predict
    response_prediction = outer_model.predict(X_test)

    # Concatenate predicted values to test data frame
    test_iteration = test_iteration.assign(prediction=response_prediction)

    # Add the test results to output data frame
    outer_results = outer_results.append(test_iteration, ignore_index=True, sort=True)
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Increase iteration number
    outer_cv_i += 1

# Partition output results to foliar cover observed and predicted
y_observed = outer_results[response[0]]
y_predicted = outer_results[prediction[0]]

# Calculate performance metrics from output_results
r_score = r2_score(y_observed, y_predicted, sample_weight=None, multioutput='uniform_average')
mae = mean_absolute_error(y_observed, y_predicted)
rmse = np.sqrt(mean_squared_error(y_observed, y_predicted))

print(r_score)
print(mae)
print(rmse)

output_csv = os.path.join(imagery_folder, 'cv_results.csv')
outer_results.to_csv(output_csv, header=True, index=False, sep=',', encoding='utf-8')
