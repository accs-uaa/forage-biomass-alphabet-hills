# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Train and test forage-site classifier
# Author: Timm Nawrocki
# Last Updated: 2022-10-24
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Train and test physiography classifier " trains a random forest model to predict physiographic types from a set of training points. This script runs the model train and test steps to output a trained classifier file and predicted data set. The train-test classifier is set to use 4 cores. The script must be run on a machine that can support 4 cores.
# ---------------------------------------------------------------------------

# Import packages
import os
import numpy as np
import pandas as pd
import joblib
import time
import datetime
from sklearn.linear_model import BayesianRidge
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import LeaveOneGroupOut

# Define round
round_date = 'round_20220607'

# Define target group
target = 'salix'

#### SET UP DIRECTORIES, FILES, AND FIELDS

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
input_file = os.path.join(data_folder,
                          'Data_Input/forage/processed/',
                          f'train_{target}.csv')
output_folder = os.path.join(data_folder, 'Data_Output/model_results', round_date, 'forage', target)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Define output data
output_csv = os.path.join(output_folder, 'prediction.csv')
output_classifier = os.path.join(output_folder, 'classifier.joblib')
importance_mdi_csv = os.path.join(output_folder, 'importance_classifier_mdi.csv')
confusion_csv = os.path.join(output_folder, 'confusion_matrix_raw.csv')

# Define variable sets
regress_variable = ['mass_g_per_m2']
predictor_all = ['fol_alnus', 'fol_betshr', 'fol_bettre', 'fol_dectre', 'fol_dryas', 'fol_empnig',
                 'fol_erivag', 'fol_picgla', 'fol_picmar', 'fol_rhoshr', 'fol_salshr', 'fol_sphagn',
                 'fol_vaculi', 'fol_vacvit', 'fol_wetsed',
                 'physio_aspen', 'physio_barren', 'physio_burned', 'physio_drainage', 'physio_riverine',
                 'physio_upland', 'physio_water']
pred_variable = ['pred_mass']
cv_groups = ['model_iteration']
outer_cv_split_n = ['outer_cv_split_n']
retain_variables = ['site_code', 'latitude_dd', 'longitude_dd']
output_variables = retain_variables + cv_groups + outer_cv_split_n \
                   + predictor_all + regress_variable + pred_variable

# Define random state
rstate = 21

#### CONDUCT MODEL TRAIN AND TEST ITERATIONS

# Create data frame of input data
input_data = pd.read_csv(input_file)
input_data['physio_riverine'] = input_data['physio_riparian'] + input_data['physio_floodplain']

# Define outer and inner cross validation splits
outer_cv_splits = LeaveOneGroupOut()
inner_cv_splits = LeaveOneGroupOut()

# Create an empty data frame to store the outer cross validation splits
outer_train = pd.DataFrame(columns=regress_variable + predictor_all)
outer_test = pd.DataFrame(columns=regress_variable + predictor_all)

# Create empty data frames to store the results across all iterations
outer_results = pd.DataFrame(columns=output_variables)

# Create outer cross validation splits
print('Creating cross validation splits...')
count = 1
for train_index, test_index in outer_cv_splits.split(input_data,
                                                     input_data[regress_variable[0]],
                                                     input_data[cv_groups[0]]):
    # Split the data into train and test partitions
    train = input_data.iloc[train_index]
    test = input_data.iloc[test_index]
    # Insert outer_cv_split_n to train
    train = train.assign(outer_cv_split_n=count)
    # Insert iteration to test
    test = test.assign(outer_cv_split_n=count)
    # Append to data frames
    outer_train = pd.concat([outer_train, train], axis=0, join='outer',
                            ignore_index=True, sort=True)
    outer_test = pd.concat([outer_test, test], axis=0, join='outer',
                           ignore_index=True, sort=True)
    # Increase counter
    count += 1
cv_length = count - 1
print(f'Created {cv_length} outer cross-validation group splits.')
print('----------')

# Iterate through outer cross validation splits
outer_cv_i = 1
while outer_cv_i <= cv_length:
    iteration_start = time.time()
    print(f'\tConducting outer cross-validation iteration {outer_cv_i} of {cv_length}...')

    #### CONDUCT MODEL TRAIN
    ####____________________________________________________

    # Partition the outer train split by iteration number
    train_iteration = outer_train.loc[outer_train[outer_cv_split_n[0]] == outer_cv_i].copy()
    test_iteration = outer_test.loc[outer_test[outer_cv_split_n[0]] == outer_cv_i].copy()

    # Reset indices
    train_iteration = train_iteration.reset_index()
    test_iteration = test_iteration.reset_index()

    # Define iteration folder
    if outer_cv_i < 10:
        iteration_folder = os.path.join(output_folder, "0" + str(outer_cv_i))
    else:
        iteration_folder = os.path.join(output_folder, str(outer_cv_i))
    if not os.path.exists(iteration_folder):
        os.mkdir(iteration_folder)

    # Identify X and y train splits for the classifier
    X_train_regress = train_iteration[predictor_all].astype(float).copy()
    y_train_regress = train_iteration[regress_variable[0]].astype(float).copy()

    # Evaluate regressor with all variables through inner cross validation
    inner_regressor = BayesianRidge()
    inner_prediction = cross_val_predict(inner_regressor, X=X_train_regress, y=y_train_regress,
                                         groups=train_iteration[cv_groups[0]], cv=inner_cv_splits)
    # Add predictions to inner data
    predict_data = pd.DataFrame(inner_prediction,
                                columns=pred_variable)
    inner_iteration = pd.concat([train_iteration, predict_data], axis=1)
    # Calculate performance metrics from output_results
    y_inner_observed = inner_iteration[regress_variable[0]]
    y_inner_predicted = inner_iteration[pred_variable[0]]
    initial_r_score = r2_score(y_inner_observed, y_inner_predicted, sample_weight=None,
                               multioutput='uniform_average')

    # Identify set of optimal predictor variables
    predictor_set = []
    predictor_remove = []
    n = 0
    while n < len(predictor_all):

        # Leave one variable out per test round
        predictor_test = predictor_all[:n] + predictor_all[n + 1:]
        X_train_regress = train_iteration[predictor_test].astype(float).copy()
        # Evaluate regressor with variable removed
        inner_prediction = cross_val_predict(inner_regressor, X=X_train_regress, y=y_train_regress,
                                             groups=train_iteration[cv_groups[0]], cv=inner_cv_splits)
        inner_data = pd.DataFrame(inner_prediction,
                                  columns=pred_variable)
        inner_iteration = pd.concat([train_iteration, inner_data], axis=1)
        y_inner_observed = inner_iteration[regress_variable[0]]
        y_inner_predicted = inner_iteration[pred_variable[0]]
        r_score = r2_score(y_inner_observed, y_inner_predicted, sample_weight=None,
                           multioutput='uniform_average')
        # Add removed predictor variable to predictor set if removal caused score to drop
        if r_score < initial_r_score:
            predictor_set.append(predictor_all[n])
        else:
            predictor_remove.append(predictor_all[n])
        # Increase counter
        n += 1

    # Export predictor set for outer cross validation iteration
    predictor_file = os.path.join(iteration_folder, 'predictor_set.txt')
    with open(predictor_file, 'w') as fp:
        for predictor in predictor_set:
            fp.write(f'{predictor}\n')

    # Train model using predictor set
    X_train_regress = train_iteration[predictor_set].astype(float).copy()
    outer_regressor = BayesianRidge()
    outer_regressor.fit(X_train_regress, y_train_regress)

    # Identify X and y test splits for the classifier
    X_test_regress = test_iteration[predictor_set].astype(float).copy()
    y_test_regress = test_iteration[regress_variable[0]].astype(float).copy()

    # Predict test data
    prediction = outer_regressor.predict(X_test_regress)
    predict_data = pd.DataFrame(prediction,
                                columns=pred_variable)

    # Add predictions to outer data
    output_iteration = pd.concat([test_iteration, predict_data], axis=1)
    outer_results = pd.concat([outer_results, output_iteration], axis=0, join='outer',
                              ignore_index=True, sort=True)

    # Save classifier to an external file
    output_classifier = os.path.join(iteration_folder, 'classifier.joblib')
    joblib.dump(outer_regressor, output_classifier)

    # Print end message
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Increase counter
    outer_cv_i += 1

# Export output results to csv with column identifying test samples
outer_results = outer_results[output_variables]
outer_results.to_csv(output_csv, header=True, index=False, sep=',', encoding='utf-8')

#### PRINT PERFORMANCE RESULTS

# Partition output results to foliar cover observed and predicted
y_regress_observed = outer_results[regress_variable[0]]
y_regress_predicted = outer_results[pred_variable[0]]

# Calculate performance metrics from output_results
r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None,
                   multioutput='uniform_average')
mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

# Report results
print('R2 = ', str(r_score))
print('MAE = ', str(mae))
print('RMSE = ', str(rmse))
