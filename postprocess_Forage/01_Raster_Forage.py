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

# Set target
target = 'alnalnsfru'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
prediction_folder = os.path.join(project_folder, 'Data_Output/predicted_tables', round_date, 'forage', target)
raster_folder = os.path.join(project_folder, 'Data_Output/predicted_rasters', round_date, 'for_' + target)
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)
if not os.path.exists(raster_folder):
    os.mkdir(raster_folder)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')

# Define output raster
output_raster = os.path.join(output_folder, 'Alphabet_forage_' + target + '.tif')

# Create key word arguments
kwargs_continuous = {'segment_folder': segment_folder,
                     'prediction_folder': prediction_folder,
                     'grid_folder': raster_folder,
                     'target_field': 'mass_g_per_m2',
                     'data_type': 'continuous',
                     'attribute_dictionary': 'NA',
                     'conversion_factor': 1,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_raster],
                     'output_array': [output_raster]
                     }

# Convert predictions to probability raster
if arcpy.Exists(output_raster) == 0:
    print(f'Converting predictions for {target} to raster...')
    arcpy_geoprocessing(predictions_to_raster, **kwargs_continuous)
    print('----------')
else:
    print(f'Raster {target} raster already exists.')
    print('----------')
