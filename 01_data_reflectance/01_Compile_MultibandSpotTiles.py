# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile multiband Spot tiles
# Author: Timm Nawrocki
# Last Updated: 2022-03-22
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Compile multiband Spot tiles" compiles blue, green, red, and infrared bands (in that order) from Spot RGB and CIR tiles.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import compile_spot_multiband

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
tile_folder = os.path.join(project_folder, 'Data_Input/imagery/spot/tiles_raw')
multiband_folder = os.path.join(project_folder, 'Data_Input/imagery/spot/tiles_processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')

# Define grids
grid_list = ['1032_1140', '1032_1142', '1032_1144',
             '1034_1140', '1034_1142', '1034_1144',
             '1036_1140', '1036_1142', '1036_1144', '1036_1146',
             '1038_1140', '1038_1142', '1038_1144', '1038_1146',
             '1040_1142', '1040_1144']

# Loop through each grid and compile multiband raster
for grid in grid_list:

    # Define input rasters
    rgb_raster = os.path.join(tile_folder, grid + '_rgb.tif')
    cir_raster = os.path.join(tile_folder, grid + '_cir.tif')

    # Define output raster
    multiband_output = os.path.join(multiband_folder, grid + '.tif')

    # Compile multiband raster for grid if it does not already exist
    if arcpy.Exists(multiband_output) == 0:
        # Create key word arguments
        kwargs_compile = {'work_geodatabase': work_geodatabase,
                          'input_array': [rgb_raster, cir_raster],
                          'output_array': [multiband_output]
                          }

        # Merge rasters
        print(f'Compiling multiband raster for grid {grid}...')
        arcpy_geoprocessing(compile_spot_multiband, **kwargs_compile)
        print('----------')

    else:
        print(f'Multiband raster already exists for grid {grid}.')
        print('----------')
