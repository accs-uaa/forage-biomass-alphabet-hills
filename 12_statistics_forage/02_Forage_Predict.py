# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Predict forage biomass to points
# Author: Timm Nawrocki
# Last Updated: 2023-03-04
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Predict forage biomass to points" predicts a random forest model to a set of grid csv files containing extracted covariate values to produce a set of output predictions with mean and standard deviation. The script must be run on a machine that can support 4 cores.
# ---------------------------------------------------------------------------

# Import packages
import glob
import joblib
import os
import pandas as pd
import time
import datetime

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
input_folder = os.path.join(data_folder, 'Data_Output/predicted_tables', round_date, 'additional')
model_folder = os.path.join(data_folder, 'Data_Output/model_results', round_date, 'forage_biomass', target)
output_folder = os.path.join(data_folder, 'Data_Output/predicted_tables', round_date, 'forage_biomass', target)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Define input files
os.chdir(input_folder)
input_files = glob.glob('*.csv')
regressor_path = os.path.join(model_folder, 'classifier.joblib')

# Define variable sets
retain_variables = ['segment_id', 'POINT_X', 'POINT_Y']
predict_variable = ['mass_g_per_m2']

# Define random state
rstate = 21

#### PREDICT FINAL REGRESSOR

# Define input files
regressor_path = os.path.join(model_folder, 'regressor.joblib')
predictor_file = os.path.join(model_folder, 'predictor_set.txt')

# Read predictor set to list
predictor_set = []
text_reader = open(predictor_file, 'r')
text_lines = text_reader.readlines()
text_reader.close()
for predictor in text_lines:
    predictor = predictor[:len(predictor) - 1]
    predictor_set.append(predictor)

# Load regressor into memory
regressor = joblib.load(regressor_path)

# Predict each input dataset
count = 1
input_length = len(input_files)
for file in input_files:
    # Define output file
    output_file = os.path.join(output_folder, os.path.split(file)[1])

    # Predict input dataset if output does not already exist
    if os.path.exists(output_file) == 0:
        print(f'Predicting input dataset {count} out of {input_length}...')

        # Load input data
        print('\tLoading input data')
        segment_start = time.time()
        all_data = pd.read_csv(file)
        # Rename physiography variables
        all_data = all_data.rename(columns={'class_01': 'physio_barren',
                                            'class_02': 'physio_burned',
                                            'class_03': 'physio_drainage',
                                            'class_04': 'physio_riparian',
                                            'class_05': 'physio_floodplain',
                                            'class_06': 'physio_water',
                                            'class_07': 'physio_upland',
                                            'class_08': 'physio_aspen'})
        # Create new variables
        all_data['physio_riverine'] = all_data['physio_riparian'] + all_data['physio_floodplain']
        # Apply correction for over-estimation of alder
        all_data['fol_alnus'] = all_data['fol_alnus'] - 10
        all_data.loc[all_data['fol_alnus'] < 0, 'fol_alnus'] = 0
        # Find where deciduous shrubs are dominant
        all_data['fol_decshr'] = all_data['fol_decshr'] - 25
        all_data.loc[all_data['fol_decshr'] < 0, 'fol_decshr'] = 0
        # Create picea variable
        all_data['fol_picea'] = all_data['fol_picgla'] + all_data['fol_picmar']
        # Select input data
        input_data = all_data[retain_variables + predictor_set].copy()
        input_data = input_data.dropna(axis=0, how='any')
        print(f'\tInput dataset contains {len(input_data)} rows...')
        X_data = input_data[predictor_set].astype(float)
        # Prepare output_data
        output_data = input_data[retain_variables]
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Predict data
        print('\tPredicting classes to points...')
        segment_start = time.time()
        prediction = regressor.predict(X_data)
        predict_data = pd.DataFrame(prediction,
                                    columns=predict_variable)

        # Add predictions to outer data
        output_data = pd.concat([output_data, predict_data], axis=1)
        # Correct negative predictions to zero
        output_data.loc[output_data[predict_variable[0]] < 0, predict_variable[0]] = 0
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Export output data to csv
        print('\tExporting predictions to csv...')
        segment_start = time.time()
        output_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

    else:
        # Return message that output already exists
        print(f'Output dataset {count} out of {input_length} already exists.')

    # Increase count
    count += 1
    print('----------')
