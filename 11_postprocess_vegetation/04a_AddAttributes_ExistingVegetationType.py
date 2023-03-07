# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add attributes for existing vegetation type
# Author: Timm Nawrocki
# Last Updated: 2023-03-03
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add attributes for existing vegetation type" adds attributes to the predicted raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import add_categorical_attributes

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
                            round_date, 'vegetation_type/Alphabet_ExistingVegetationType.tif')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/data_package',
                             version_number, 'vegetation_type/Alphabet_ExistingVegetationType_Attributed.tif')

# Define surficial features dictionary
class_values = {'barren': 1,
                'sparsely vegetated': 2,
                'water': 3,
                'balsam poplar floodplain (white spruce)': 4,
                'white spruce floodplain': 5,
                'alder - willow floodplain': 6,
                'black spruce - Alaska birch - Sphagnum': 7,
                'black spruce, mesic': 8,
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
                'boreal montane herbaceous': 21,
                'boreal herbaceous': 22,
                'unclassified': 23
                }

# Create key word arguments
kwargs_attributes = {'attribute_dictionary': class_values,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [study_raster, input_raster],
                     'output_array': [output_raster]
                     }

# Add attributes
print(f'Attributing raster...')
arcpy_geoprocessing(add_categorical_attributes, **kwargs_attributes)
print('----------')
