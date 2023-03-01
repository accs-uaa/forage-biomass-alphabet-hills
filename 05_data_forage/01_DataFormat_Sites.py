# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format sites
# Author: Timm Nawrocki
# Last Updated: 2022-10-24
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format sites" prepares a table of point data for feature extraction by selecting appropriate raster cells based on cell size.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import format_site_data
from package_GeospatialProcessing import table_to_feature_projected

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
sites_folder = os.path.join(project_folder, 'Data_Input/forage/unprocessed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alph_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
alph_feature = os.path.join(work_geodatabase, 'Alphabet_StudyArea')
sites_file = os.path.join(sites_folder, '02_site_accsalphabethills2021.csv')

# Define output point feature class
sites_feature = os.path.join(work_geodatabase, 'Forage_Sites_AKALB')
sites_formatted = os.path.join(work_geodatabase, 'Forage_Sites_Formatted_AKALB')

# Convert sites csv table to point feature class if it does not already exist
if arcpy.Exists(sites_feature) == 0:

    # Create key word arguments
    kwargs_table = {'input_projection': 4269,
                    'output_projection': 3338,
                    'geographic_transformation': '',
                    'work_geodatabase': work_geodatabase,
                    'input_array': [alph_feature, sites_file],
                    'output_array': [sites_feature]
                    }

    # Convert table to points
    print(f'Converting table to projected points feature class for study area...')
    arcpy_geoprocessing(table_to_feature_projected, **kwargs_table)
    print('----------')

else:
    print('Projected points feature class for study area already exists.')
    print('----------')

# Format site data if it does not already exist
if arcpy.Exists(sites_formatted) == 0:

    # Create key word arguments
    kwargs_format = {'work_geodatabase': work_geodatabase,
                     'input_array': [sites_feature, alph_raster],
                     'output_array': [sites_formatted]
                     }

    # Format site data
    print(f'Formatting site data...')
    arcpy_geoprocessing(format_site_data, **kwargs_format)
    print('----------')

else:
    print('Formatted data already exists.')
    print('----------')
