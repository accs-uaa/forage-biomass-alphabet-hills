# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create cross-validation grid
# Author: Timm Nawrocki
# Last Updated: 2022-03-26
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create cross-validation grid" creates a validation grid index from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import parse_image_segments
from package_GeospatialProcessing import create_grid_index
from package_GeospatialProcessing import convert_validation_grid
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')
segments_geodatabase = os.path.join(project_folder, 'AlphabetHills_Segments.gdb')

# Define input datasets
alphabet_feature = os.path.join(work_geodatabase, 'Alphabet_StudyArea')
alphabet_raster = os.path.join(project_folder, 'Data_Input/Alphabet_StudyArea.tif')
segments_point = os.path.join(work_geodatabase, 'Alphabet_Segments_Final_Point')
segments_polygon = os.path.join(work_geodatabase, 'Alphabet_Segments_Final_Polygon')

# Define output grid datasets
validation_grid = os.path.join(work_geodatabase, 'Alphabet_GridIndex_Validation_10km')
validation_raster = os.path.join(project_folder, 'Data_Input/validation/Alphabet_ValidationGroups.tif')
grid_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')

#### GENERATE VALIDATION GRID INDEX

# Create key word arguments for the validation grid index
validation_kwargs = {'distance': '10 Kilometers',
                     'grid_field': 'grid_validation',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_feature],
                     'output_array': [validation_grid]
                     }

# Create the validation grid index
if arcpy.Exists(validation_grid) == 0:
    print('Creating validation grid index...')
    arcpy_geoprocessing(create_grid_index, **validation_kwargs)
    print('----------')
else:
    print('Validation grid index already exists.')
    print('----------')

#### CONVERT VALIDATION GRIDS TO RASTERS

# Create key word arguments for validation raster
raster_kwargs = {'work_geodatabase': work_geodatabase,
                 'input_array': [validation_grid, alphabet_feature, alphabet_raster],
                 'output_array': [validation_raster]
                 }

# Generate validation group raster
if arcpy.Exists(validation_raster) == 0:
    print('Converting validation grids to raster for North American Beringia...')
    arcpy_geoprocessing(convert_validation_grid, **raster_kwargs)
    print('----------')
else:
    print('Validation raster already exists.')
    print('----------')

#### PARSE REFINED IMAGE SEGMENTS FOR VALIDATION GRIDS

parse_kwargs = {'tile_name': 'grid_validation',
                'work_geodatabase': segments_geodatabase,
                'input_array': [alphabet_raster, validation_grid, segments_point, segments_polygon],
                'output_folder': grid_folder
                }

# Create buffered tiles for the major grid
arcpy_geoprocessing(parse_image_segments, check_output=False, **parse_kwargs)
print('----------')
