# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Predict forage biomass to points
# Author: Timm Nawrocki
# Last Updated: 2022-10-28
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

# Import functions from repository statistics package
from package_Statistics import multiclass_predict

# Define round
round_date = 'round_20220607'

#### SET UP DIRECTORIES, FILES, AND FIELDS

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
input_folder = os.path.join(data_folder, 'Data_Input/training/table')
model_folder = os.path.join(data_folder, 'Data_Output/model_results', round_date, 'physiography')
output_folder = os.path.join(data_folder, 'Data_Output/predicted_tables', round_date, 'physiography')

# Define input files
os.chdir(input_folder)
input_files = glob.glob('*.csv')
classifier_path = os.path.join(model_folder, 'classifier.joblib')

# Define variable sets
regress_variable = ['mass_g_per_m2']
predictor_all = ['fol_alnus', 'fol_betshr', 'fol_bettre', 'fol_dectre', 'fol_dryas', 'fol_empnig',
                 'fol_erivag', 'fol_picgla', 'fol_picmar', 'fol_rhoshr', 'fol_salshr', 'fol_sphagn',
                 'fol_vaculi', 'fol_vacvit', 'fol_wetsed',
                 'physio_aspen', 'physio_barren', 'physio_burned', 'physio_drainage', 'physio_riverine',
                 'physio_upland', 'physio_water', 'ws_ratio',
                 'aspect', 'elevation', 'wetness']
retain_variables = ['segment_id', 'POINT_X', 'POINT_Y',
                    'fol_alnus', 'fol_betshr', 'fol_bettre', 'fol_dectre', 'fol_dryas', 'fol_empnig', 'fol_erivag',
                    'fol_picgla', 'fol_picmar', 'fol_rhoshr', 'fol_salshr', 'fol_sphagn', 'fol_vaculi', 'fol_vacvit',
                    'fol_wetsed']
prediction = ['physiography']
output_columns = retain_variables + predictor_all

# Define random state
rstate = 21

# Load model into memory
print('Loading classifier into memory...')
segment_start = time.time()
classifier = joblib.load(classifier_path)
# Report success
segment_end = time.time()
segment_elapsed = int(segment_end - segment_start)
segment_success_time = datetime.datetime.now()
print(f'Completed at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
print('----------')

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
        input_data = all_data[retain_variables + class_variable + predictor_all].copy()
        input_data = input_data.dropna(axis=0, how='any')
        print(f'\tInput dataset contains {len(input_data)} rows...')
        X_data = input_data[predictor_all].astype(float)
        # Prepare output_data
        output_data = input_data[output_columns]
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Predict data
        print('\tPredicting classes to points...')
        segment_start = time.time()
        output_data = multiclass_predict(classifier, X_data, prediction, class_number, output_data)
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Export output data to csv
        print('\tExporting predictions to csv...')
        segment_start = time.time()
        output_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

    else:
        # Return message that output already exists
        print(f'Output dataset {count} out of {input_length} already exists.')

    # Increase count
    count += 1
    print('----------')