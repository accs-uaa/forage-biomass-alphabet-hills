# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create physiography rasters
# Author: Timm Nawrocki
# Last Updated: 2022-03-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create physiography raster" combines tiles into a physiography raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import predictions_to_raster

# Set round date
round_date = 'round_20220327'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
prediction_folder = os.path.join(project_folder, 'Data_Output/predicted_tables', round_date)
grid_folder = os.path.join(project_folder, 'Data_Output/predicted_rasters', round_date, 'physiography')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')

# Define output raster
output_raster = os.path.join(output_folder, 'Alphabet_Physiography.tif')

# Create key word arguments
kwargs_attributes = {'segment_folder': segment_folder,
                     'prediction_folder': prediction_folder,
                     'grid_folder': grid_folder,
                     'target_field': 'physiography',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_raster],
                     'output_array': [output_raster]
                     }

# Convert predictions to physiography raster
print(f'Converting predictions to physiography raster...')
arcpy_geoprocessing(predictions_to_raster, **kwargs_attributes)
print('----------')