# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge high-resolution imagery composites
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Merge high-resolution imagery composites" combines Maxar and Spot-5 imagery composites with Spot-5 imagery selected by a manually defined mask raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import extract_raster
from package_GeospatialProcessing import merge_segmentation_imagery

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
maxar_folder = os.path.join(project_folder, 'Data_Input/imagery/maxar/composite')
spot_folder = os.path.join(project_folder, 'Data_Input/imagery/spot/composite')
composite_folder = os.path.join(project_folder, 'Data_Input/imagery/composite')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')
maxar_mask = os.path.join(project_folder, 'Data_Input/imagery/maxar/maxar_mask.tif')
maxar_image = os.path.join(maxar_folder, 'Alphabet_MaxarComposite_AKALB.tif')
spot_image = os.path.join(spot_folder, 'Alphabet_SpotComposite_AKALB.tif')

# Define output datasets
spot_extract = os.path.join(spot_folder, 'Alphabet_SpotComposite_Extract.tif')
composite_image = os.path.join(composite_folder, 'Alphabet_Composite_AKALB.tif')

#### EXTRACT SPOT IMAGERY

# Create key word arguments
kwargs_extract = {'work_geodatabase': work_geodatabase,
                  'input_array': [alphabet_raster, spot_image, maxar_mask],
                  'output_array': [spot_extract]
                  }

# Extract raster
print('Extracting Spot-5 imagery...')
arcpy_geoprocessing(extract_raster, **kwargs_extract)
print('----------')

#### MERGE SEGMENTATION IMAGERY

# Create key word arguments
kwargs_merge = {'input_projection': 3338,
                'work_geodatabase': work_geodatabase,
                'input_array': [alphabet_raster, spot_extract, maxar_image],
                'output_array': [composite_image]
                }

# Merge segmentation imagery
print('Merging segmentation imagery...')
arcpy_geoprocessing(merge_segmentation_imagery, **kwargs_merge)
print('----------')
