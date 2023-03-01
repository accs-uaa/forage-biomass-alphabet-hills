# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize vegetation abundance rasters
# Author: Timm Nawrocki
# Last Updated: 2022-12-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7+ installation.
# Description: "Summarize vegetation abundance rasters" calculates the zonal mean of vegetation rasters.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_zonal_statistics

# Set round date
round_date = 'round_20221219'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/BLM_AIM/GMT-2/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/processed')
input_folder = os.path.join(project_folder, 'Data_Input/vegetation_pattern')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'GMT2_Workspace.gdb')

# Define input datasets
grid_raster = os.path.join(segment_folder, 'GMT2_Segments_Revised.tif')

#### CREATE CONTINUOUS VEGETATION ABUNDANCE

# Define class list and physiography list
input_list = ['NorthAmericanBeringia_alnus_A6', 'NorthAmericanBeringia_betshr_A6',
              'NorthAmericanBeringia_dryas_A6', 'NorthAmericanBeringia_empnig_A6',
              'NorthAmericanBeringia_erivag_A6', 'NorthAmericanBeringia_rhoshr_A6',
              'NorthAmericanBeringia_salshr_A6', 'NorthAmericanBeringia_sphagn_A6',
              'NorthAmericanBeringia_vaculi_A6', 'NorthAmericanBeringia_vacvit_A6',
              'NorthAmericanBeringia_wetsed_A6']
output_list = ['GMT2_foliar_alnus', 'GMT2_foliar_betshr', 'GMT2_foliar_dryas',
               'GMT2_foliar_empnig', 'GMT2_foliar_erivag', 'GMT2_foliar_rhoshr',
               'GMT2_foliar_salshr', 'GMT2_foliar_sphagn', 'GMT2_foliar_vaculi',
               'GMT2_foliar_vacvit', 'GMT2_foliar_wetsed']

# Iterate through each class and export a continuous abundance raster
input_length = len(input_list)
input_range = range(0, input_length, 1)
for i in input_range:
    # Define input raster
    input_raster = os.path.join(input_folder, input_list[i] + '.tif')
    # Define output raster
    output_raster = os.path.join(output_folder, output_list[i] + '.tif')

    # Create output raster if it does not already exist
    if arcpy.Exists(output_raster) == 0:
        # Create key word arguments
        kwargs_zonal = {'statistic': 'MEAN',
                        'zone_field': 'VALUE',
                        'work_geodatabase': work_geodatabase,
                        'input_array': [grid_raster, input_raster],
                        'output_array': [output_raster]
                        }

        # Process the zonal summaries
        print(f'\tProcessing zonal summary {i} of {input_length}...')
        arcpy_geoprocessing(calculate_zonal_statistics, **kwargs_zonal)
        print('\t----------')
    else:
        print(f'{input_list[i]} raster already exists.')
        print('----------')
