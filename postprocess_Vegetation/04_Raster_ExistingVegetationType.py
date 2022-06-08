# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create existing vegetation type rasters
# Author: Timm Nawrocki
# Last Updated: 2022-04-21
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create existing vegetation type rasters" combines tiles into a vegetation type raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import predictions_to_raster

# Set round date
round_date = 'round_20220331'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
prediction_folder = os.path.join(project_folder, 'Data_Output/modified_tables', round_date)
grid_folder = os.path.join(project_folder, 'Data_Output/predicted_rasters', round_date, 'evt')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')

# Define output raster
output_raster = os.path.join(output_folder, 'Alphabet_ExistingVegetationType.tif')

# Define EVT dictionary
evt_dictionary = {'Barren': 1,
                  'Sparsely Vegetated': 2,
                  'Water': 3,
                  'Aspen / White Spruce - Aspen': 4,
                  'Birch': 5,
                  'Black Spruce - Alaska Birch - Sphagnum': 6,
                  'Black Spruce, Mesic (Inactive Floodplain)': 7,
                  'Black Spruce, Hygric (- Hydric)': 8,
                  'White Spruce Floodplain': 9,
                  'White Spruce - Alder': 10,
                  'White Spruce - Birch Shrub': 11,
                  'White Spruce - Willow': 12,
                  'Spruce (- Alaska Birch)': 13,
                  'Alder - Willow Floodplain': 14,
                  'Alder - Willow': 15,
                  'Birch Shrub - Willow, Mesic': 16,
                  'Birch Shrub - Willow, Hygric (- Hydric)': 17,
                  'Ericaceous Dwarf Shrub - Dryas': 18,
                  'Sedge Wetland': 19,
                  'Unclassified Floodplain': 20,
                  'Unclassified Herbaceous': 21,
                  'Unclassified': 22
                  }

# Create key word arguments
kwargs_attributes = {'segment_folder': segment_folder,
                     'prediction_folder': prediction_folder,
                     'grid_folder': grid_folder,
                     'target_field': 'evt_value',
                     'attribute_dictionary': evt_dictionary,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_raster],
                     'output_array': [output_raster]
                     }

# Convert predictions to EVT raster
print(f'Converting predictions to EVT raster...')
arcpy_geoprocessing(predictions_to_raster, **kwargs_attributes)
print('----------')
