# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic properties
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic properties" calculates integer versions of ten topographic indices for each grid using elevation float rasters.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_topographic_properties

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
input_folder = os.path.join(project_folder, 'Data_Input/topography/float')
output_folder = os.path.join(project_folder, 'Data_Input/topography/integer')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/AlphabetHills_StudyArea.tif')
elevation_float = os.path.join(input_folder, 'Elevation.tif')

# Define output datasets
elevation_integer = os.path.join(output_folder, 'Elevation.tif')
slope_integer = os.path.join(output_folder, 'Slope.tif')
aspect_integer = os.path.join(output_folder, 'Aspect.tif')
exposure_output = os.path.join(output_folder, 'Exposure.tif')
heatload_output = os.path.join(output_folder, 'HeatLoad.tif')
position_output = os.path.join(output_folder, 'Position.tif')
radiation_output = os.path.join(output_folder, 'Radiation.tif')
roughness_output = os.path.join(output_folder, 'Roughness.tif')
surfacearea_output = os.path.join(output_folder, 'SurfaceArea.tif')
surfacerelief_output = os.path.join(output_folder, 'SurfaceRelief.tif')
wetness_output = os.path.join(output_folder, 'Wetness.tif')

# Create key word arguments
kwargs_topography = {'z_unit': 'METER',
                     'position_width': 5000,
                     'input_array': [alphabet_raster, elevation_float],
                     'output_array': [elevation_integer,
                                      slope_integer,
                                      aspect_integer,
                                      exposure_output,
                                      heatload_output,
                                      position_output,
                                      radiation_output,
                                      roughness_output,
                                      surfacearea_output,
                                      surfacerelief_output,
                                      wetness_output]
                     }

# Process the topographic calculations
print(f'Processing topography...')
arcpy_geoprocessing(calculate_topographic_properties, **kwargs_topography, check_output=False)
print('----------')
