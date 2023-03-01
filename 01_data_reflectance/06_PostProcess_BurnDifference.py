# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process burn difference raster
# Author: Timm Nawrocki
# Last Updated: 2022-03-29
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process burn difference raster" reprojects raster, converts to integer, and extracts to the study area.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import fnmatch
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import reproject_extract
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
unprocessed_folder = os.path.join(project_folder, 'Data_Input/imagery/burn/unprocessed')
processed_folder = os.path.join(project_folder, 'Data_Input/imagery/burn/processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
input_raster = os.path.join(unprocessed_folder, 'burn_diff.tif')

# Define output datasets
output_raster = os.path.join(processed_folder, 'burn_diff.tif')

# Reset environment workspace
arcpy.env.workspace = work_geodatabase

#### PROCESS IMAGERY RASTERS

# Set conversion factor
conversion_factor = 10000

# Create key word arguments
kwargs_reproject = {'cell_size': 10,
                    'input_projection': 4326,
                    'output_projection': 3338,
                    'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                    'conversion_factor': conversion_factor,
                    'input_array': [alphabet_raster, input_raster],
                    'output_array': [output_raster]
                    }

# Process the reproject integer function
print(f'Processing burn difference using conversion factor {conversion_factor}...')
arcpy_geoprocessing(reproject_extract, **kwargs_reproject)
print('----------')
