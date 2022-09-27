# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create vegetation abundance rasters
# Author: Timm Nawrocki
# Last Updated: 2022-08-18
# Usage: Must be executed in an ArcGIS Pro Python 3.7+ installation.
# Description: "Create vegetation abundance rasters" combines tiles into rasters of predicted vegetation abundance per image segment.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import predictions_to_raster

# Set round date
round_date = 'round_20220607'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
prediction_folder = os.path.join(project_folder, 'Data_Output/predicted_tables', round_date, 'physiography')
raster_folder = os.path.join(project_folder, 'Data_Output/predicted_rasters', round_date)
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')

#### CREATE CONTINUOUS VEGETATION ABUNDANCE

# Define class list and physiography list
class_list = ['fol_alnus', 'fol_betshr', 'fol_bettre', 'fol_dectre', 'fol_dryas', 'fol_empnig', 'fol_erivag', 'fol_picgla',
              'fol_picmar', 'fol_rhoshr', 'fol_salshr', 'fol_sphagn', 'fol_vaculi', 'fol_vacvit', 'fol_wetsed']

# Iterate through each class and export a continuous abundance raster
count = 1
for class_label in class_list:
    # Define and create physiography directory
    abundance_folder = os.path.join(raster_folder, class_label)
    if os.path.exists(abundance_folder) == 0:
        os.mkdir(abundance_folder)

    # Define output raster
    continuous_output = os.path.join(output_folder, f'Alphabet_{class_label}.tif')

    # Create key word arguments
    kwargs_continuous = {'segment_folder': segment_folder,
                         'prediction_folder': prediction_folder,
                         'grid_folder': abundance_folder,
                         'target_field': class_label,
                         'data_type': 'continuous',
                         'attribute_dictionary': 'NA',
                         'conversion_factor': 1,
                         'work_geodatabase': work_geodatabase,
                         'input_array': [alphabet_raster],
                         'output_array': [continuous_output]
                         }

    # Convert predictions to abundance raster
    if arcpy.Exists(continuous_output) == 0:
        print(f'Converting abundance predictions for {class_label} to raster...')
        arcpy_geoprocessing(predictions_to_raster, **kwargs_continuous)
        print('----------')
    else:
        print(f'{class_label.capitalize()} raster already exists.')
        print('----------')

    # Increase count
    count += 1