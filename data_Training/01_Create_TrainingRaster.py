# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2022-03-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create training raster" creates a raster of training data values from a set of manually delineated polygons representing different types for a classification.
# ---------------------------------------------------------------------------

# Import packages
import sys

sys.path.append('C:/Users/timmn/Documents/Repositories/alphabet-hills-moose-browse/')
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import convert_class_data

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
training_folder = os.path.join(project_folder, 'Data_Input/training_data/processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
class_feature = os.path.join(work_geodatabase, 'Alphabet_Physiography')

# Define output datasets
class_raster = os.path.join(training_folder, 'Alphabet_Physiography.tif')

# Define fields
class_field = 'physiography'

# Define class values
class_values = {
    'barren': 1,
    'burned': 2,
    'drainage': 3,
    'riparian': 4,
    'floodplain': 5,
    'water': 6,
    'upland/lowland': 7,
    'aspen': 8
}

#### CREATE TRAINING RASTER

# Create key word arguments
kwargs_training = {'class_field': class_field,
                   'value_dictionary': class_values,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [alphabet_raster, class_feature],
                   'output_array': [class_raster]
                   }

# Convert polygon class data to raster
print(f'Converting polygon class data to raster...')
arcpy_geoprocessing(convert_class_data, **kwargs_training)
print('----------')
