# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process floodplains
# Author: Timm Nawrocki
# Last Updated: 2022-03-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process floodplains" creates a set of approximate floodplain boundaries from flowline position.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_floodplains

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
hydrography_folder = os.path.join(project_folder, 'Data_Input/hydrography')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')
river_feature = os.path.join(work_geodatabase, 'Alphabet_Rivers_DEM_Corrected')
stream_feature = os.path.join(work_geodatabase, 'Alphabet_Streams_DEM_Corrected')
river_position = os.path.join(hydrography_folder, 'River_Position.tif')
stream_position = os.path.join(hydrography_folder, 'Stream_Position.tif')

# Define output datasets
floodplain_raster = os.path.join(hydrography_folder, 'Floodplain.tif')
floodplain_feature = os.path.join(work_geodatabase, 'Alphabet_Floodplains')

#### MERGE FLOODPLAINS FROM RIVERS AND STREAMS

# Create key word arguments
kwargs_floodplain = {'thresholds': [400, 9],
                     'area_limit': 2000000,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_raster, river_feature, stream_feature, river_position, stream_position],
                     'output_array': [floodplain_raster, floodplain_feature]
                     }

# Post-process segments
if arcpy.Exists(floodplain_feature) == 0:
    print('Calculate topographic floodplains...')
    arcpy_geoprocessing(merge_floodplains, **kwargs_floodplain)
    print('----------')
else:
    print('Floodplains already exist.')
    print('----------')
