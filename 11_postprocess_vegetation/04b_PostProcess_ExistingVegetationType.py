# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process existing vegetation type
# Author: Timm Nawrocki
# Last Updated: 2023-02-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process existing vegetation type" processes the predicted raster into the final deliverable.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_categorical_raster

# Set round date
round_date = 'round_20220607'
version_number = 'v1_0'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')
work_geodatabase = os.path.join(project_folder, 'AlphabetHills_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
input_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                            round_date, 'vegetation_type', 'Alphabet_ExistingVegetationType.tif')
river_raster = os.path.join(project_folder, 'Data_Input/hydrography/processed/Rivers.tif')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/data_package', version_number, 'vegetation_type',
                             'Alphabet_ExistingVegetationType.tif')

# Define EVT dictionary
class_values = {'barren': 1,
                'sparsely vegetated': 2,
                'water': 3,
                'balsalm poplar floodplain (white spruce)': 3,
                'white spruce floodplain': 4,
                'alder - willow floodplain': 5,
                'boreal herbaceous floodplain, mesic': 6,
                'black spruce - Alaska birch - Sphagnum': 7,
                'black spruce, mesic (inactive floodplain)': 8,
                'black spruce, wet': 9,
                'white spruce - alder': 10,
                'white spruce - birch shrub': 11,
                'white spruce - willow': 12,
                'mixed spruce (- Alaska birch)': 13,
                'aspen / white spruce - aspen': 14,
                'birch': 15,
                'alder - willow': 16,
                'birch shrub - willow, mesic': 17,
                'birch shrub - willow, wet': 18,
                'montane Dryas-ericaceous dwarf shrub, acidic': 19,
                'boreal sedge meadow, wet': 20,
                'boreal/boreal-montane herbaceous': 21,
                'unclassified': 22
                }

# Create key word arguments
kwargs_process = {'minimum_count': 505,
                  'water_value': 3,
                  'null_statement': 'VALUE = 22',
                  'attribute_dictionary': class_values,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [study_raster, input_raster, river_raster],
                  'output_array': [output_raster]
                  }

# Post-process EVT raster
print(f'Post-processing EVT raster...')
arcpy_geoprocessing(postprocess_categorical_raster, **kwargs_process)
print('----------')
