# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile Spot multiband raster
# Author: Timm Nawrocki
# Last Updated: 2022-01-12
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Compile Spot multiband raster" is a function that combines rgb and cir spot rasters into blue, green, red, infrared multiband rasters.
# ---------------------------------------------------------------------------

# Define a function to parse spot data into multiband rasters
def compile_spot_multiband(**kwargs):
    """
    Description: parses spot data into multiband rasters
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the rgb raster (must be first) and the cir raster (must be second)
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires a pair of Spot rasters
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import time
    import os

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    rgb_raster = kwargs['input_array'][0]
    cir_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set snap raster and extent
    arcpy.env.snapRaster = rgb_raster
    arcpy.env.extent = Raster(rgb_raster).extent

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Make raster layer and export as new raster
    print('\tParsing raster bands to new rasters...')
    iteration_start = time.time()
    blue_layer = 'blue_band_raster'
    green_layer = 'green_band_raster'
    red_layer = 'red_band_raster'
    infrared_layer = 'infrared_band_raster'
    arcpy.management.MakeRasterLayer(rgb_raster,
                                     blue_layer,
                                     '',
                                     'MAXOF',
                                     3)
    arcpy.management.MakeRasterLayer(rgb_raster,
                                     green_layer,
                                     '',
                                     'MAXOF',
                                     2)
    arcpy.management.MakeRasterLayer(rgb_raster,
                                     red_layer,
                                     '',
                                     'MAXOF',
                                     1)
    arcpy.management.MakeRasterLayer(cir_raster,
                                     infrared_layer,
                                     '',
                                     'MAXOF',
                                     1)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Composite raster bands to multiband raster
    print('\tCompositing raster bands...')
    iteration_start = time.time()
    arcpy.management.CompositeBands([blue_layer, green_layer, red_layer, infrared_layer],
                                    output_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Report success
    out_process = 'Successfully compiled multiband raster.'
    return out_process
