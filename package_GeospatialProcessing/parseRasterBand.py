# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse raster band
# Author: Timm Nawrocki
# Last Updated: 2022-01-03
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Parse raster bands" is a function that parses a band from a multi-band raster to a new single-band raster.
# ---------------------------------------------------------------------------

# Define a function to parse multi-band raster to single-band raster for specified band
def parse_raster_band(**kwargs):
    """
    Description: parses a band from multi-band raster to new single-band raster
    Inputs: 'band' -- the target band number
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the input raster
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires an image composite raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    band = kwargs['band']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    composite_raster = kwargs['input_array'][1]
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

    # Make raster layer and export as new raster
    print('\tParsing raster band to new raster...')
    iteration_start = time.time()
    raster_layer = 'single_band_raster'
    arcpy.management.MakeRasterLayer(composite_raster,
                                     raster_layer,
                                     '',
                                     area_raster,
                                     band
                                     )
    arcpy.management.CopyRaster(raster_layer,
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
    out_process = 'Successfully parsed raster to single band.'
    return out_process
