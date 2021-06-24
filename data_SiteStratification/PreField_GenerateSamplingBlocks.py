# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Terrestrial Sampling Blocks
# Author: Timm Nawrocki
# Last Updated: 2021-06-23
# Usage: Must be executed in an ArcGIS Pro Python 3.6+ installation.
# Description: "Generate Terrestrial Sampling Blocks" prepares a set of sampling blocks from manually generated points or polygons and removes lakes.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_sample_block

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
work_geodatabase = os.path.join(data_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define lakes feature class
lakes_feature = os.path.join(work_geodatabase, 'AlphabetHills_Waterbodies')

# Define starting units
lake_1_1 = os.path.join(work_geodatabase, 'Lake_1_1')
lake_1_2 = os.path.join(work_geodatabase, 'Lake_1_2')
lake_1_3 = os.path.join(work_geodatabase, 'Lake_1_3')
lake_2_1 = os.path.join(work_geodatabase, 'Lake_2_1')
lake_2_2 = os.path.join(work_geodatabase, 'Lake_2_2')
lake_3_1 = os.path.join(work_geodatabase, 'Lake_3_1')
lake_3_2 = os.path.join(work_geodatabase, 'Lake_3_2')
lake_4_1 = os.path.join(work_geodatabase, 'Lake_4_1')
lake_4_2 = os.path.join(work_geodatabase, 'Lake_4_2')

# Make list of starting units
starting_units = [lake_1_1, lake_1_2, lake_1_3, lake_2_1, lake_2_2, lake_3_1, lake_3_2, lake_4_1, lake_4_2]

# Loop through all starting units and generate sampling blocks
for unit in starting_units:
    # Name output block
    output_block = unit.replace('Lake', 'Block')
    block = os.path.split(output_block)[1]

    # Determine if output block already exists
    if arcpy.Exists(output_block) == 0:
        # Define input and output arrays
        block_inputs = [unit, lakes_feature]
        block_outputs = [output_block]

        # Create key word arguments
        block_kwargs = {'buffer_distance': '800 METERS',
                        'subdivide_number': 4,
                        'work_geodatabase': work_geodatabase,
                        'input_array': block_inputs,
                        'output_array': block_outputs
                        }

        # Create sample block
        print(f'Creating {block}...')
        arcpy_geoprocessing(create_sample_block, **block_kwargs)
        print('----------')

    else:
        print(f'{block} already exists.')
        print('----------')
