# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate flowlines
# Author: Timm Nawrocki
# Last Updated: 2022-01-17
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Generate flowlines" is a function that calculates flowlines from a float elevation raster.
# ---------------------------------------------------------------------------

# Define a function to generate flowlines.
def generate_flowlines(**kwargs):
    """
    Description: generates flowlines from a float elevation raster
    Inputs: 'threshold' -- flow accumulation threshold for minimum stream size
            'fill_value' -- a value in the vertical units of the elevation raster to set as the fill limit
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area feature class (must be first), the float elevation raster (must be second), and an optional mask raster (if present, must be last)
            'output_array' -- an array containing the the river feature class and the stream feature class
    Returned Value: Returns a set filled elevation raster and a set of flowline feature classes on disk
    Preconditions: requires an input elevation raster that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Fill
    from arcpy.sa import FlowAccumulation
    from arcpy.sa import FlowDirection
    from arcpy.sa import Raster
    from arcpy.sa import StreamOrder
    import datetime
    import os
    import time

    # Parse key word argument inputs
    threshold = kwargs['threshold']
    fill_value = kwargs['fill_value']
    work_geodatabase = kwargs['work_geodatabase']
    area_feature = kwargs['input_array'][0]
    elevation_raster = kwargs['input_array'][1]
    river_feature = kwargs['output_array'][1]
    stream_feature = kwargs['output_array'][2]

    # Define intermediate dataset
    topography_folder = os.path.split(elevation_raster)[0]
    area_buffer = os.path.join(work_geodatabase, 'StudyArea_Buffer_5km')
    buffer_raster = os.path.join(topography_folder, 'Buffer_Raster.tif')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = elevation_raster

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(elevation_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Buffer study area
    print('\tCreating calculation area...')
    iteration_start = time.time()
    arcpy.analysis.PairwiseBuffer(area_feature,
                                  area_buffer,
                                  '10 Kilometers',
                                  'NONE',
                                  '',
                                  'PLANAR')
    arcpy.conversion.PolygonToRaster(area_feature,
                                     'OBJECTID',
                                     buffer_raster,
                                     'CELL_CENTER',
                                     '',
                                     cell_size,
                                     'BUILD')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Extract elevation to calculation area
    print('\tExtracting elevation raster...')
    iteration_start = time.time()
    elevation_extract = ExtractByMask(Raster(elevation_raster), buffer_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Fill elevation
    print('\tFilling elevation raster...')
    iteration_start = time.time()
    fill_raster = Fill(elevation_extract, fill_value)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate flow direction
    print('\tCalculating flow direction...')
    iteration_start = time.time()
    direction_raster = FlowDirection(fill_raster, 'NORMAL', '', 'D8')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate flow accumulation
    print('\tCalculating flow accumulation...')
    iteration_start = time.time()
    accumulation_raster = FlowAccumulation(direction_raster, '', 'FLOAT', 'D8')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Apply threshold to the flow accumulation
    print('\tDefining stream network from flow accumulation...')
    iteration_start = time.time()
    stream_definition = f'VALUE >= {threshold}'
    stream_raster = Con(accumulation_raster, 1, '', stream_definition)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate stream order
    print('\tDefining stream order...')
    iteration_start = time.time()
    stream_order = StreamOrder(stream_raster, direction_raster, 'STRAHLER')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # If a mask raster is supplied, then extract the stream order
    if len(kwargs['input_array']) == 3:
        print('\tExtracting stream order to mask...')
        iteration_start = time.time()
        # Define mask raster
        mask_raster = kwargs['input_array'][2]
        # Extract flow accumulation to mask raster
        final_raster = ExtractByMask(stream_order, mask_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    # If no mask is specified, then use full raster
    else:
        final_raster = stream_order

    # Convert stream order to flowline feature classes
    print('\tConverting raster stream order to flowline feature classes...')
    iteration_start = time.time()
    # Convert streams
    stream_raster = Con(final_raster, 1, '', 'VALUE <= 3')
    arcpy.conversion.RasterToPolyline(stream_raster,
                                      stream_feature,
                                      'NODATA',
                                      0,
                                      'SIMPLIFY')
    # Convert rivers
    river_raster = Con(final_raster, 1, '', 'VALUE > 3')
    arcpy.conversion.RasterToPolyline(river_raster,
                                      river_feature,
                                      'NODATA',
                                      0,
                                      'SIMPLIFY')
    # Delete intermediate datasets
    if arcpy.Exists(buffer_raster) == 1:
        arcpy.management.Delete(buffer_raster)
    if arcpy.Exists(area_buffer) == 1:
        arcpy.management.Delete(area_buffer)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tFinished at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully created flowlines.'
    return outprocess
