# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Select Field Sample Sites Per Block
# Author: Timm Nawrocki
# Last Updated: 2021-06-23
# Usage: Must be executed in an ArcGIS Pro Python 3.6+ installation.
# Description: "Select Field Sample Sites Per Block" prepares a probability raster and performs spatially balanced site selection for a set of manually generated sampling blocks.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import probabilistic_site_selection

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
work_geodatabase = os.path.join(data_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input rasters
raster_salix = os.path.join(data_folder, 'Data_Input/vegetation/salshr.tif')

# Define study area
study_area = os.path.join(data_folder, 'Data_Input/Alphabet_StudyArea.tif')

# Define sampling blocks
block_1_1 = os.path.join(work_geodatabase, 'Block_1_1')
block_1_2 = os.path.join(work_geodatabase, 'Block_1_2')
block_1_3 = os.path.join(work_geodatabase, 'Block_1_3')
block_2_1 = os.path.join(work_geodatabase, 'Block_2_1')
block_2_2 = os.path.join(work_geodatabase, 'Block_2_2')
block_3_1 = os.path.join(work_geodatabase, 'Block_3_1')
block_3_2 = os.path.join(work_geodatabase, 'Block_3_2')
block_4_1 = os.path.join(work_geodatabase, 'Block_4_1')
block_4_2 = os.path.join(work_geodatabase, 'Block_4_2')

# Make list of sampling block subdivisions
subdivision_number = 4
sampling_blocks = [block_1_1, block_1_2, block_1_3, block_2_1, block_2_2, block_3_1, block_3_2, block_4_1, block_4_2]
sampling_units = []
for block in sampling_blocks:
    count = 1
    while count <= subdivision_number:
        sampling_units.append(block + f'_{str(count)}')
        count += 1

# Loop through all sampling units and generate spatially balanced points
for unit in sampling_units:
    # Name output points
    output_points = unit.replace('Block', 'Sites')
    unit_name = os.path.split(unit)[1]

    # Determine if output points already exist
    if arcpy.Exists(output_points) == 0:
        # Define input and output arrays
        site_inputs = [study_area, raster_salix, unit]
        site_outputs = [output_points]

        # Create key word arguments
        site_kwargs = {'number_points': 20,
                       'work_geodatabase': work_geodatabase,
                       'input_array': site_inputs,
                       'output_array': site_outputs
                       }

        # Select sites for block
        print(f'Selecting field sites for {unit_name}...')
        arcpy_geoprocessing(probabilistic_site_selection, **site_kwargs)
        print('----------')

    else:
        print(f'Selected sites already exist for {unit_name}.')
        print('----------')
