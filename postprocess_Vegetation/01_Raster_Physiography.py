# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create physiography rasters
# Author: Timm Nawrocki
# Last Updated: 2022-06-07
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create physiography rasters" combines tiles into a discrete physiography raster and probabilistic class rasters.
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

# Define output raster
output_raster = os.path.join(output_folder, 'Alphabet_Physiography.tif')

#### CREATE DISCRETE PHYSIOGRAPHY

# Define and create physiography directory
physiography_folder = os.path.join(raster_folder, 'physiography')
if os.path.exists(physiography_folder) == 0:
    os.mkdir(physiography_folder)

# Define output raster
discrete_output = os.path.join(output_folder, 'Alphabet_Physiography.tif')

# Define physiography dictionary
physiography_dictionary = {'barren': 1,
                           'burned': 2,
                           'drainage': 3,
                           'riparian': 4,
                           'floodplain': 5,
                           'water': 6,
                           'upland/lowland': 7,
                           'aspen': 8
                           }

# Create key word arguments
kwargs_discrete = {'segment_folder': segment_folder,
                   'prediction_folder': prediction_folder,
                   'grid_folder': physiography_folder,
                   'target_field': 'physiography',
                   'data_type': 'discrete',
                   'attribute_dictionary': physiography_dictionary,
                   'conversion_factor': 'NA',
                   'work_geodatabase': work_geodatabase,
                   'input_array': [alphabet_raster],
                   'output_array': [discrete_output]
                   }

# Convert predictions to physiography raster
if arcpy.Exists(discrete_output) == 0:
    print(f'Converting discrete predictions to physiography raster...')
    arcpy_geoprocessing(predictions_to_raster, **kwargs_discrete)
    print('----------')
else:
    print('Discrete raster already exists.')
    print('----------')

#### CREATE CONTINUOUS PHYSIOGRAPHY PROBABILITY

# Define class list and physiography list
class_list = ['class_01', 'class_02', 'class_03', 'class_04',
              'class_05', 'class_06', 'class_07', 'class_08']
physiography_list = ['barren', 'burned', 'drainage', 'riparian',
                     'floodplain', 'water', 'upland-Lowland', 'aspen']

# Iterate through each class and export a continuous probability raster
count = 1
for class_label in class_list:
    # Identify corresponding physiography label
    physiography_label = physiography_list[count - 1]

    # Define and create physiography directory
    probability_folder = os.path.join(raster_folder, physiography_label)
    if os.path.exists(probability_folder) == 0:
        os.mkdir(probability_folder)

    # Define output raster
    physiography_name = physiography_label.capitalize()
    continuous_output = os.path.join(output_folder, f'Alphabet_PhysioProbability_{physiography_name}.tif')

    # Create key word arguments
    kwargs_continuous = {'segment_folder': segment_folder,
                         'prediction_folder': prediction_folder,
                         'grid_folder': probability_folder,
                         'target_field': class_label,
                         'data_type': 'continuous',
                         'attribute_dictionary': 'NA',
                         'conversion_factor': 1000,
                         'work_geodatabase': work_geodatabase,
                         'input_array': [alphabet_raster],
                         'output_array': [continuous_output]
                         }

    # Convert predictions to probability raster
    if arcpy.Exists(continuous_output) == 0:
        print(f'Converting probability predictions for {physiography_label} to raster...')
        arcpy_geoprocessing(predictions_to_raster, **kwargs_continuous)
        print('----------')
    else:
        print(f'{physiography_name} raster already exists.')
        print('----------')

    # Increase count
    count += 1
