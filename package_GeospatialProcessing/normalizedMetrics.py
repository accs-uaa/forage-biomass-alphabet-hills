# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate normalized metrics
# Author: Timm Nawrocki
# Last Updated: 2022-01-03
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate normalized metrics" is a function that calculates normalized difference spectral metrics and enhanced vegetation index-2.
# ---------------------------------------------------------------------------

# Define a function to calculate spectral metrics
def normalized_metrics(**kwargs):
    """
    Description: calculates normalized metrics and EVI2 from specified bands
    Inputs: 'type' -- a string value of either "EVI2" or "NORMALIZED"
            'conversion_factor' -- a number that will be multiplied with the original value before being converted to integer
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the additive raster, and the subtractive raster
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires an single band image rasters
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    metric_type = kwargs['metric_type']
    conversion_factor = kwargs['conversion_factor']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    add_raster = kwargs['input_array'][1]
    subtract_raster = kwargs['input_array'][2]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Calculate spectral metric
    iteration_start = time.time()
    if metric_type == 'EVI2':
        print('\tCalculating EVI2...')
        metric_raster = (Raster(add_raster) - Raster(subtract_raster)) / (1 + Raster(add_raster) + (2.4 * Raster(subtract_raster)))
    else:
        print('\tCalculating normalized difference metric...')
        metric_raster = (Raster(add_raster) - Raster(subtract_raster)) / (Raster(add_raster) + Raster(subtract_raster))
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Convert to integer raster and export
    print('\tConverting to integer and exporting...')
    iteration_start = time.time()
    integer_raster = Int((metric_raster * conversion_factor) + 0.5)
    arcpy.management.CopyRaster(integer_raster,
                                output_raster,
                                '',
                                '',
                                '-2147483648',
                                'NONE',
                                'NONE',
                                '32_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Report success
    out_process = f'Successfully calculated {metric_type} metric.'
    return out_process
