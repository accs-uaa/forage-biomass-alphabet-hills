# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Train and test vegetation classifier
# Author: Timm Nawrocki
# Last Updated: 2022-01-20
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Train and test vegetation classifier " trains a random forest model to predict vegetation and land surface types from a set of training points. This script runs the model train and test steps to output a trained classifier file and predicted data set. The train-test classifier is set to use 4 cores. The script must be run on a machine that can support 4 cores.
# ---------------------------------------------------------------------------

# Import packages
import os
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut
import time
import datetime

# Import functions from repository statistics package
from package_Statistics import multiclass_train_test

# Define round
round_date = 'round_20220120'

#### SET UP DIRECTORIES, FILES, AND FIELDS

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
data_input = os.path.join(data_folder, 'Data_Input/training_data')
data_output = os.path.join(data_folder, 'Data_Output/model_results', round_date)

# Define input file
input_file = os.path.join(data_input, 'AllPoints_ExtractedCovariates.csv')

# Define output data
output_csv = os.path.join(data_output, 'prediction.csv')
output_classifier = os.path.join(data_output, 'classifier.joblib')
importance_mdi_csv = os.path.join(data_output, 'importance_classifier_mdi.csv')
confusion_csv = os.path.join(data_output, 'confusion_matrix.csv')

# Define variable sets
class_variable = ['class_value']
predictor_all = ['aspect', 'elevation', 'exposure', 'heat_load', 'position', 'radiation', 'roughness', 'slope',
                 'surface_area', 'surface_relief', 'wetness',
                 'river_position', 'stream_position',
                 'comp_01_blue', 'comp_02_green', 'comp_03_red', 'comp_04_nearir', 'comp_evi2', 'comp_ndvi', 'comp_ndwi',
                 'comp_01_blue_std', 'comp_02_green_std', 'comp_03_red_std', 'comp_04_nearir_std',
                 'comp_evi2_std', 'comp_ndvi_std', 'comp_ndwi_std',
                 'vh', 'vv',
                 's2_06_02_blue', 's2_06_03_green', 's2_06_04_red', 's2_06_05_rededge1', 's2_06_06_rededge2',
                 's2_06_07_rededge3', 's2_06_08_nearir', 's2_06_08a_rededge4', 's2_06_11_shortir1', 's2_06_12_shortir2',
                 's2_06_evi2', 's2_06_nbr', 's2_06_ndmi', 's2_06_ndsi', 's2_06_ndvi', 's2_06_ndwi',
                 's2_07_02_blue', 's2_07_03_green', 's2_07_04_red', 's2_07_05_rededge1', 's2_07_06_rededge2',
                 's2_07_07_rededge3', 's2_07_08_nearir', 's2_07_08a_rededge4', 's2_07_11_shortir1', 's2_07_12_shortir2',
                 's2_07_evi2', 's2_07_nbr', 's2_07_ndmi', 's2_07_ndsi', 's2_07_ndvi', 's2_07_ndwi',
                 's2_08_02_blue', 's2_08_03_green', 's2_08_04_red', 's2_08_05_rededge1', 's2_08_06_rededge2',
                 's2_08_07_rededge3', 's2_08_08_nearir', 's2_08_08a_rededge4', 's2_08_11_shortir1', 's2_08_12_shortir2',
                 's2_08_evi2', 's2_08_nbr', 's2_08_ndmi', 's2_08_ndsi', 's2_08_ndvi', 's2_08_ndwi',
                 's2_09_02_blue', 's2_09_03_green', 's2_09_04_red', 's2_09_05_rededge1', 's2_09_06_rededge2',
                 's2_09_07_rededge3', 's2_09_08_nearir', 's2_09_08a_rededge4', 's2_09_11_shortir1', 's2_09_12_shortir2',
                 's2_09_evi2', 's2_09_nbr', 's2_09_ndmi', 's2_09_ndsi', 's2_09_ndvi', 's2_09_ndwi']
cv_groups = ['cv_group']
retain_variables = ['gridcode', 'POINT_X', 'POINT_Y']
outer_cv_split_n = ['outer_cv_split_n']
prediction = ['prediction']
output_variables = class_variable + predictor_all + outer_cv_split_n + prediction

# Define random state
rstate = 21

#### CONDUCT MODEL TRAIN AND TEST ITERATIONS

# Create a standardized parameter set for a random forest classifier
classifier_params = {'n_estimators': 1000,
                     'criterion': 'gini',
                     'max_depth': None,
                     'min_samples_split': 2,
                     'min_samples_leaf': 1,
                     'min_weight_fraction_leaf': 0,
                     'max_features': 'sqrt',
                     'bootstrap': False,
                     'oob_score': False,
                     'warm_start': False,
                     'class_weight': 'balanced',
                     'n_jobs': 4,
                     'random_state': rstate}

# Create data frame of input data
data_all = pd.read_csv(input_file)
input_data = data_all[data_all[class_variable[0]] > 0].copy()

# Define leave one group out cross validation split methods
outer_cv_splits = LeaveOneGroupOut()

# Create empty data frames to store the results across all iterations
output_results = pd.DataFrame(columns=output_variables)
importances_all = pd.DataFrame(columns=['covariate', 'importance'])

# Conduct model train and test for iteration
outer_results, trained_classifier, importance_table = multiclass_train_test(classifier_params,
                                                                            input_data,
                                                                            class_variable,
                                                                            predictor_all,
                                                                            cv_groups,
                                                                            retain_variables,
                                                                            outer_cv_splits,
                                                                            rstate,
                                                                            output_classifier)

# Print results of model train and test
print(f'Outer results contain {len(outer_results)} rows.')
print('----------')

#### STORE RESULTS

# Store output results in csv file
print('Saving combined results to csv file...')
iteration_start = time.time()
outer_results.to_csv(output_csv, header=True, index=False, sep=',', encoding='utf-8')
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
print(
    f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Store output importances in csv file
print('Saving variable importances to csv file...')
iteration_start = time.time()
importance_table.to_csv(importance_mdi_csv, header=True, index=False, sep=',', encoding='utf-8')
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
print(
    f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Calculate and store confusion matrix
print('Saving confusion matrix to csv file...')
iteration_start = time.time()
# Assign true and predicted values
true_data = outer_results[class_variable[0]]
pred_data = outer_results[prediction[0]]
# Create confusion matrix
confusion_data = pd.crosstab(true_data, pred_data, rownames=['Actual'], colnames=['Predicted'], margins=True)
# Export confusion matrix
confusion_data.to_csv(confusion_csv, header=True, index=True, sep=',', encoding='utf-8')
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
print(
    f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')
