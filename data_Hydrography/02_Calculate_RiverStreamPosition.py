# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate river and stream position
# Author: Timm Nawrocki
# Last Updated: 2022-01-17
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate river and stream position" calculates river and stream position from a river feature class, stream feature class, and filled elevation raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import generate_hydrographic_position

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
topography_folder = os.path.join(project_folder, 'Data_Input/topography/float')
hydrography_folder = os.path.join(project_folder, 'Data_Input/hydrography')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')
elevation_raster = os.path.join(topography_folder, 'Elevation.tif')
river_feature = os.path.join(work_geodatabase, 'Alphabet_Rivers_DEM_Corrected')
stream_feature = os.path.join(work_geodatabase, 'Alphabet_Streams_DEM_Corrected')

# Define output datasets
river_raster = os.path.join(hydrography_folder, 'River_Position.tif')
stream_raster = os.path.join(hydrography_folder, 'Stream_Position.tif')

#### CALCULATE RIVER POSITION

# Create key word arguments
kwargs_river = {'work_geodatabase': work_geodatabase,
                'input_array': [alphabet_raster, elevation_raster, river_feature],
                'output_array': [river_raster]
                }

# Process the river flowlines
print(f'Processing river flowlines...')
arcpy_geoprocessing(generate_hydrographic_position, **kwargs_river)
print('----------')

#### CALCULATE STREAM POSITION

# Create key word arguments
kwargs_stream = {'work_geodatabase': work_geodatabase,
                 'input_array': [alphabet_raster, elevation_raster, stream_feature],
                 'output_array': [stream_raster]
                 }

# Process the river flowlines
print(f'Processing stream flowlines...')
arcpy_geoprocessing(generate_hydrographic_position, **kwargs_stream)
print('----------')
