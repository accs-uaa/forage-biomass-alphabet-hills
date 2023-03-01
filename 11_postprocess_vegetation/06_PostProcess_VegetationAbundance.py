# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process vegetation abundance
# Author: Timm Nawrocki
# Last Updated: 2022-12-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process vegetation abundance" corrects vegetation abundance according to predicted surface types.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_continuous_raster

# Set round date
round_date = 'round_20221219'
version_number = 'v1_0'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/BLM_AIM/GMT-2/Data')
input_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date, 'vegetation_pattern')
output_folder = os.path.join(project_folder, 'Data_Output/data_package', version_number, 'vegetation_pattern')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'GMT2_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/GMT2_StudyArea.tif')
evt_raster = os.path.join(project_folder, 'Data_Output/output_rasters', round_date, 'vegetation_type',
                          'GMT2_ExistingVegetationType.tif')
infrastructure_raster = os.path.join(project_folder, 'Data_Input/infrastructure/Infrastructure_Developed.tif')

# Create empty list for input rasters
input_rasters = []

# Create list of vegetation rasters
arcpy.env.workspace = input_folder
vegetation_rasters = arcpy.ListRasters('*', 'TIF')
for raster in vegetation_rasters:
    raster_path = os.path.join(input_folder, raster)
    input_rasters.append(raster_path)

# Loop through each input raster and post-process to output raster
count = 1
input_length = len(input_rasters)
for input_raster in input_rasters:
    # Define output raster
    output_raster = os.path.join(output_folder, os.path.split(input_raster)[1])

    # Create output raster if it does not already exist
    if arcpy.Exists(output_raster) == 0:
        # Define conditional statement
        if os.path.split(input_raster)[1] == 'GMT2_foliar_alnus.tif':
            conditional_statement = 'VALUE <> 19 And VALUE <> 20'
        elif os.path.split(input_raster)[1] == 'GMT2_foliar_wetsed.tif':
            conditional_statement = 'VALUE = 1 Or VALUE = 2'
        elif os.path.split(input_raster)[1] == 'GMT2_foliar_sphagn.tif':
            conditional_statement = 'VALUE = 1 Or VALUE = 2'
        else:
            conditional_statement = 'VALUE = 1 Or VALUE = 2 Or VALUE = 5'

        # Create key word arguments
        kwargs_process = {'calculate_mean': False,
                          'conditional_statement': conditional_statement,
                          'data_type': '8_BIT_SIGNED',
                          'work_geodatabase': work_geodatabase,
                          'input_array': [study_raster, evt_raster, infrastructure_raster, input_raster],
                          'output_array': [output_raster]
                          }

        # Post-process vegetation abundance rasters
        print(f'Post-processing raster {count} of {input_length}...')
        arcpy_geoprocessing(postprocess_continuous_raster, **kwargs_process)
        print('----------')
    else:
        print(f'Raster {count} of {input_length} already exists.')
        print('----------')
    count += 1
