# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Composite segmentation imagery
# Author: Timm Nawrocki
# Last Updated: 2022-02-15
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Composite segmentation imagery" is a function that merges tiles into a composite raster and then reprojects to a target resolution and grid.
# ---------------------------------------------------------------------------

# Define a function to merge and reproject imagery for segmentation
def composite_segmentation_imagery(**kwargs):
    """
    Description: merges imagery into a single multi-band raster and reprojects
    Inputs: 'cell_size' -- a cell size for the output spectral raster
            'output_projection' -- the machine number for the output projection
            'input_projection' -- the machine number for the input projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'conversion_factor' -- a number that will be multiplied with the original value before being converted to integer
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the input rasters
            'output_array' -- an array containing the output rasters
    Returned Value: Returns a raster datasets on disk containing the full raster composite at original projection and resolution and the segmentation raster reprojected and extracted to the area raster
    Preconditions: requires source spectral tiles and predefined area raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import IsNull
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    conversion_factor = kwargs['conversion_factor']
    input_rasters = kwargs['input_array']
    area_raster = input_rasters.pop(0)
    composite_raster = kwargs['output_array'][0]
    segmentation_raster = kwargs['output_array'][1]

    # Define intermediate datasets
    mosaic_raster = os.path.splitext(composite_raster)[0] + '_mosaic.tif'
    reprojected_raster = os.path.splitext(composite_raster)[0] + '_reprojected.tif'

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set initial snap raster
    arcpy.env.snapRaster = input_rasters[1]

    # Define the input and output coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    output_system = arcpy.SpatialReference(output_projection)

    # Define mosaic name and location
    mosaic_location, mosaic_name = os.path.split(mosaic_raster)

    # Determine number of bands in rasters
    band_count = arcpy.Describe(Raster(input_rasters[1])).bandCount
    original_size = arcpy.management.GetRasterProperties(input_rasters[1], 'CELLSIZEX').getOutput(0)

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking input rasters with {band_count} bands...')
    # Check if mosaic raster already exists
    if arcpy.Exists(mosaic_raster) == 0:
        iteration_start = time.time()
        arcpy.management.MosaicToNewRaster(input_rasters,
                                           mosaic_location,
                                           mosaic_name,
                                           input_system,
                                           '32_BIT_SIGNED',
                                           original_size,
                                           band_count,
                                           'MAXIMUM',
                                           'FIRST')
        # Enforce correct projection
        arcpy.management.DefineProjection(mosaic_raster, input_system)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    # If mosaic raster already exists, report message
    else:
        print('\tMosaic raster already exists.')
        print('\t----------')

    # Check if composite raster exists
    print('\tEnforcing correct no data values...')
    if arcpy.Exists(composite_raster) == 0:
        # Enforce correct values
        iteration_start = time.time()
        con_raster = Con(IsNull(Raster(mosaic_raster)), 255, Raster(mosaic_raster))
        arcpy.management.CopyRaster(con_raster,
                                    composite_raster,
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
    # If composite raster already exists, report message
    else:
        print('\tComposite raster already exists.')
        print('\t----------')

    # Set final snap raster
    arcpy.env.snapRaster = area_raster

    # Project raster to output coordinate system
    print(f'\tReprojecting composite raster...')
    # Check if projected raster already exists
    if arcpy.Exists(segmentation_raster) == 0:
        iteration_start = time.time()
        # Multiply composite raster by conversion factor
        converted_raster = Raster(composite_raster) * conversion_factor
        # Reproject raster
        arcpy.management.ProjectRaster(converted_raster,
                                       reprojected_raster,
                                       output_system,
                                       'BILINEAR',
                                       cell_size,
                                       geographic_transformation,
                                       '',
                                       input_system)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success for iteration
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

        # Extract reprojected raster to area raster
        print('\tExtracting imagery composite to study area...')
        iteration_start = time.time()
        raster_extract = ExtractByMask(reprojected_raster, area_raster)
        arcpy.management.CopyRaster(raster_extract,
                                    segmentation_raster,
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
        # Delete intermediate rasters
        if arcpy.Exists(reprojected_raster) == 1:
            arcpy.management.Delete(reprojected_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
        out_process = f'Successfully created composite and segmentation rasters.'
    # If composite raster already exists, report message
    else:
        print('\tSegmentation raster already exists.')
        print('\t----------')
        out_process = 'Segmentation imagery not produced.'
    # Return message
    return out_process
