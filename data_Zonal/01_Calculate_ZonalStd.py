# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate zonal standard deviations
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate zonal standard deviations" calculates zonal standard deviations of input datasets to segments defined in a raster.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_zonal_statistics

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
composite_folder = os.path.join(project_folder, 'Data_Input/imagery/composite/processed')
output_folder = os.path.join(project_folder, 'Data_Input/zonal')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_TestArea.tif')
zone_raster = os.path.join(project_folder, 'Data_Input/imagery/segments/processed/Alphabet_Segments_Test.tif')

# Create empty raster list
input_rasters = []

# Create list of Maxar rasters
arcpy.env.workspace = composite_folder
composite_rasters = arcpy.ListRasters('*', 'TIF')
for raster in composite_rasters:
    raster_path = os.path.join(composite_folder, raster)
    input_rasters.append(raster_path)

# Set workspace to default
arcpy.env.workspace = work_geodatabase

# Create zonal summary for each raster in input list
count = 1
raster_length = len(input_rasters)
for input_raster in input_rasters:

    # Define output raster
    raster_name = os.path.split(input_raster)[1]
    output_raster = os.path.join(output_folder, os.path.splitext(raster_name)[0] + '_STD.tif')

    # Create zonal summary if output raster does not already exist
    if arcpy.Exists(output_raster) == 0:

        # Create key word arguments
        kwargs_zonal = {'statistic': 'STD',
                        'zone_field': 'VALUE',
                        'work_geodatabase': work_geodatabase,
                        'input_array': [alphabet_raster, input_raster, zone_raster],
                        'output_array': [output_raster]
                        }

        # Process the zonal summaries
        print(f'Processing zonal summary {count} of {raster_length}...')
        arcpy_geoprocessing(calculate_zonal_statistics, **kwargs_zonal)
        print('----------')

    # If raster already exists, print message
    else:
        print(f'Zonal summary {count} of {raster_length} already exists.')
        print('----------')

    # Increase counter
    count += 1
