# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge segmentation imagery
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Merge segmentation imagery" is a function that merges composite images to combine two or more image sources according to an order or priority.
# ---------------------------------------------------------------------------

# Define a function to merge imagery for segmentation
def merge_segmentation_imagery(**kwargs):
    """
    Description: merges imagery into a single multi-band raster
    Inputs: 'input_projection' -- the machine number for the input projection
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the input rasters in order of priority
            'output_array' -- an array containing the output rasters
    Returned Value: Returns a raster dataset on disk containing the composite image raster
    Preconditions: requires imagery composites all with the same number and order of bands
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    input_projection = kwargs['input_projection']
    work_geodatabase = kwargs['work_geodatabase']
    input_rasters = kwargs['input_array']
    area_raster = input_rasters.pop(0)
    composite_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Define the input coordinate system
    input_system = arcpy.SpatialReference(input_projection)

    # Define mosaic name and location
    mosaic_location, mosaic_name = os.path.split(composite_raster)

    # Determine number of bands in rasters
    band_count = arcpy.Describe(Raster(input_rasters[1])).bandCount
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX').getOutput(0)

    # Determine input raster value type
    value_number = arcpy.management.GetRasterProperties(input_rasters[1], "VALUETYPE").getOutput(0)
    if band_count > 1:
        no_data_value = arcpy.Describe(input_rasters[1] + '/Band_1').noDataValue
    else:
        no_data_value = arcpy.Describe(input_rasters[1]).noDataValue
    value_dictionary = {
        0: '1_BIT',
        1: '2_BIT',
        2: '4_BIT',
        3: '8_BIT_UNSIGNED',
        4: '8_BIT_SIGNED',
        5: '16_BIT_UNSIGNED',
        6: '16_BIT_SIGNED',
        7: '32_BIT_UNSIGNED',
        8: '32_BIT_SIGNED',
        9: '32_BIT_FLOAT',
        10: '64_BIT'
    }
    value_type = value_dictionary.get(int(value_number))
    print(f'\tOutput data type will be {value_type}.')
    print(f'\tOutput no data value will be {no_data_value}.')
    print('\t----------')

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking input rasters with {band_count} bands...')
    iteration_start = time.time()
    arcpy.management.MosaicToNewRaster(input_rasters,
                                       mosaic_location,
                                       mosaic_name,
                                       input_system,
                                       value_type,
                                       cell_size,
                                       band_count,
                                       'FIRST',
                                       'FIRST')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully merged imagery composites.'
    return out_process
