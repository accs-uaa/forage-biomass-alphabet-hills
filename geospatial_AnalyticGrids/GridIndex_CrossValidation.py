# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create cross-validation grid
# Author: Timm Nawrocki
# Last Updated: 2022-01-17
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create cross-validation grid" creates a validation grid index from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_grid_index
from package_GeospatialProcessing import convert_validation_grid
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_feature = os.path.join(work_geodatabase, 'AlphabetHills_StudyArea')
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')

# Define output grid datasets
validation_grid = os.path.join(work_geodatabase, 'Alphabet_GridIndex_Validation_5km')
validation_raster = os.path.join(project_folder, 'Data_Input/validation/Alphabet_ValidationGroups.tif')

#### GENERATE VALIDATION GRID INDEX

# Create key word arguments for the validation grid index
validation_kwargs = {'distance': '5 Kilometers',
                     'grid_field': 'grid_validation',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_feature],
                     'output_array': [validation_grid]
                     }

# Create the validation grid index
if arcpy.Exists(validation_grid) == 0:
    print('Creating validation grid index...')
    arcpy_geoprocessing(create_grid_index, **validation_kwargs)
    print('----------')
else:
    print('Validation grid index already exists.')
    print('----------')

#### CONVERT VALIDATION GRIDS TO RASTERS

# Create key word arguments for validation raster
raster_kwargs = {'work_geodatabase': work_geodatabase,
                 'input_array': [validation_grid, alphabet_feature, alphabet_raster],
                 'output_array': [validation_raster]
                 }

# Generate validation group raster for North American Beringia
if arcpy.Exists(validation_raster) == 0:
    print('Converting validation grids to raster for North American Beringia...')
    arcpy_geoprocessing(convert_validation_grid, **raster_kwargs)
    print('----------')
else:
    print('Validation raster already exists.')
    print('----------')
