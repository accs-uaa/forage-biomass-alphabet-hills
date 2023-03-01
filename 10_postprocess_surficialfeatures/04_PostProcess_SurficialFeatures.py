# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process surficial features
# Author: Timm Nawrocki
# Last Updated: 2023-02-22
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process surficial features" processes the predicted raster into the final deliverable.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_categorical_raster

# Set round date
round_date = 'round_20220607'
version_number = 'v1_0'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')
work_geodatabase = os.path.join(project_folder, 'AlphabetHills_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
input_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                            round_date, 'surficial_features', 'Alphabet_SurficialFeatures.tif')
river_raster = os.path.join(project_folder, 'Data_Input/hydrography/processed/Rivers.tif')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/data_package', version_number, 'surficial_features',
                             'Alphabet_SurficialFeatures.tif')

# Define surficial features dictionary
class_values = {'barren': 1,
                'burned': 2,
                'drainage': 3,
                'riparian': 4,
                'floodplain': 5,
                'water': 6,
                'upland/lowland': 7,
                'aspen': 8}

# Create key word arguments
kwargs_process = {'minimum_count': 505,
                  'water_value': 6,
                  'attribute_dictionary': class_values,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [study_raster, input_raster, river_raster],
                  'output_array': [output_raster]
                  }

# Post-process surficial features raster
print(f'Post-processing surficial features raster...')
arcpy_geoprocessing(postprocess_categorical_raster, **kwargs_process)
print('----------')
