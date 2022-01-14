# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process Sentinel-2 rasters
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process Sentinel-2 rasters" reprojects rasters, converts to integer, and extracts to the study area.
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
unprocessed_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-2/unprocessed')
processed_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-2/processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')

# List imagery tiles
print('Searching for imagery tiles...')
# Start timing function
iteration_start = time.time()
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = unprocessed_folder
# Create a raster list using the Arcpy List Rasters function
unprocessed_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
unprocessed_rasters = []
for raster in unprocessed_list:
    raster_path = os.path.join(unprocessed_folder, raster)
    unprocessed_rasters.append(raster_path)
rasters_length = len(unprocessed_rasters)
print(f'{rasters_length} imagery rasters will be processed...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Reset environment workspace
arcpy.env.workspace = work_geodatabase

#### PROCESS IMAGERY RASTERS

# Set initial raster count
count = 1

# Reproject all imagery rasters
for input_raster in unprocessed_rasters:
    # Define processed raster
    output_raster = os.path.join(processed_folder, os.path.split(input_raster)[1])

    # Reproject and convert tile if processed tile does not already exist
    if arcpy.Exists(output_raster) == 0:
        # Determine conversion factor
        if (fnmatch.fnmatch(output_raster, '*evi2*')
                or fnmatch.fnmatch(output_raster, '*nbr*')
                or fnmatch.fnmatch(output_raster, '*ndmi*')
                or fnmatch.fnmatch(output_raster, '*ndsi*')
                or fnmatch.fnmatch(output_raster, '*ndvi*')
                or fnmatch.fnmatch(output_raster, '*ndwi*')):
            conversion_factor = 1000000
        else:
            conversion_factor = 10

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
        print(f'Processing tile {count} of {rasters_length} using conversion factor {conversion_factor}...')
        arcpy_geoprocessing(reproject_extract, **kwargs_reproject)
        print('----------')
    else:
        print(f'Tile {count} of {rasters_length} already exists.')
        print('----------')

    # Increase counter
    count += 1
