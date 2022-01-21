# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate zonal means
# Author: Timm Nawrocki
# Last Updated: 2022-01-16
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate zonal means" calculates zonal means of input datasets to segments defined in a raster.
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
topography_folder = os.path.join(project_folder, 'Data_Input/topography/integer')
hydrography_folder = os.path.join(project_folder, 'Data_Input/hydrography')
sent1_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-1/processed')
sent2_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-2/processed')
composite_folder = os.path.join(project_folder, 'Data_Input/imagery/composite/processed')
vegetation_folder = os.path.join(project_folder, 'Data_Input/vegetation/foliar_cover')
output_folder = os.path.join(project_folder, 'Data_Input/zonal')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_TestArea.tif')
zone_raster = os.path.join(project_folder, 'Data_Input/imagery/segments/processed/Alphabet_Segments_Test.tif')

# Create empty raster list
input_rasters = []

# Create list of topography rasters
arcpy.env.workspace = topography_folder
topography_rasters = arcpy.ListRasters('*', 'TIF')
for raster in topography_rasters:
    raster_path = os.path.join(topography_folder, raster)
    input_rasters.append(raster_path)

# Create list of hydrography rasters
arcpy.env.workspace = hydrography_folder
hydrography_rasters = arcpy.ListRasters('*', 'TIF')
for raster in hydrography_rasters:
    raster_path = os.path.join(hydrography_folder, raster)
    input_rasters.append(raster_path)

# Create list of Sentinel-1 rasters
arcpy.env.workspace = sent1_folder
sent1_rasters = arcpy.ListRasters('*', 'TIF')
for raster in sent1_rasters:
    raster_path = os.path.join(sent1_folder, raster)
    input_rasters.append(raster_path)

# Create list of Sentinel-2 rasters
arcpy.env.workspace = sent2_folder
sent2_rasters = arcpy.ListRasters('*', 'TIF')
for raster in sent2_rasters:
    raster_path = os.path.join(sent2_folder, raster)
    input_rasters.append(raster_path)

# Create list of composite rasters
arcpy.env.workspace = composite_folder
composite_rasters = arcpy.ListRasters('*', 'TIF')
for raster in composite_rasters:
    raster_path = os.path.join(composite_folder, raster)
    input_rasters.append(raster_path)

# Create list of vegetation rasters
arcpy.env.workspace = vegetation_folder
vegetation_rasters = arcpy.ListRasters('*', 'TIF')
for raster in vegetation_rasters:
    raster_path = os.path.join(vegetation_folder, raster)
    input_rasters.append(raster_path)

# Set workspace to default
arcpy.env.workspace = work_geodatabase

# Create zonal summary for each raster in input list
count = 1
raster_length = len(input_rasters)
for input_raster in input_rasters:

    # Define output raster
    raster_name = os.path.split(input_raster)[1]
    output_raster = os.path.join(output_folder, raster_name)

    # Create zonal summary if output raster does not already exist
    if arcpy.Exists(output_raster) == 0:

        # Create key word arguments
        kwargs_zonal = {'statistic': 'MEAN',
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
