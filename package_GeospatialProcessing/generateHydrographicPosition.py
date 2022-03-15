# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate hydrographic position
# Author: Timm Nawrocki
# Last Updated: 2022-03-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Generate hydrographic position" is a function that calculates the vertical difference between flowline elevation and landscape elevation from a float elevation raster and a set of flowlines, which can be derived from a DEM, the NHD, or manual delineation (or some combination thereof).
# ---------------------------------------------------------------------------

# Define a function to generate hydrographic position.
def generate_hydrographic_position(**kwargs):
    """
    Description: calculates hydrographic position from a float elevation raster and a set of flowlines
    Inputs: 'distance' -- a string of numerical distance and unit representing search distance from flowline
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster, the float elevation raster, and the flowlines (in that order)
            'output_array' -- an array containing the hydrographic position raster
    Returned Value: Returns a raster on disk
    Preconditions: requires input elevation and flowlines that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import IsNull
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    distance = kwargs['distance']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    elevation_raster = kwargs['input_array'][1]
    flowline_feature = kwargs['input_array'][2]
    hydrography_raster = kwargs['output_array'][0]

    # Define intermediate dataset
    hydrography_folder = os.path.split(hydrography_raster)[0]
    flowline_raster = os.path.join(hydrography_folder, 'Flowlines.tif')
    preliminary_raster = os.path.join(hydrography_folder, 'Preliminary.tif')
    flowline_buffered = os.path.join(work_geodatabase, 'flowlines_buffered')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "25%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(elevation_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Extract elevation to calculation area
    print('\tExtracting elevation raster...')
    iteration_start = time.time()
    elevation_extract = ExtractByMask(Raster(elevation_raster), area_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Extract elevation to flowlines
    print('\tCalculating flowline position...')
    iteration_start = time.time()
    # Convert stream network to raster
    print('\t\tConverting flowline network to raster...')
    arcpy.conversion.PolylineToRaster(flowline_feature,
                                      'grid_code',
                                      flowline_raster,
                                      'MAXIMUM_LENGTH',
                                      '',
                                      cell_size,
                                      'BUILD')
    # Extract elevation to stream network
    print('\t\tExtracting elevation to flowlines...')
    flowline_elevation = ExtractByMask(elevation_extract, Raster(flowline_raster))
    # Expand stream elevation
    print('\t\tExpanding flowline elevation...')
    flowline_position = Nibble(flowline_elevation, Raster(flowline_raster), 'DATA_ONLY', 'PROCESS_NODATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate hydrographic position
    print('\tCalculating hydrographic position...')
    iteration_start = time.time()
    hydrographic_position = ((elevation_extract - flowline_position) * (elevation_extract - flowline_position)) * 100
    # Control for excessively high values
    limit_raster = Con(hydrographic_position, Int(hydrographic_position + 0.5), 32000, 'VALUE < 32000')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Extract to flowline buffer
    print('\tRestricting results to search distance...')
    iteration_start = time.time()
    # Create flowline buffer
    print('\t\tCreating flowline buffer...')
    arcpy.analysis.PairwiseBuffer(flowline_feature,
                                  flowline_buffered,
                                  distance,
                                  'NONE',
                                  '',
                                  'PLANAR')
    # Extract hydrographic position to buffer
    print('\t\tExtracting hydrographic position to buffer...')
    position_extract = ExtractByMask(limit_raster, flowline_buffered)
    # Convert no data to 32000
    print('\t\tConverting no data to maximum...')
    corrected_raster = Con(IsNull(position_extract), 32000, position_extract)
    # Export final raster
    print('\t\tExporting preliminary raster...')
    arcpy.management.CopyRaster(corrected_raster,
                                preliminary_raster,
                                '',
                                '',
                                '-32768',
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # Extract preliminary raster to final raster
    print('\t\tExtracting preliminary raster...')
    final_raster = ExtractByMask(preliminary_raster, area_raster)
    # Export final raster
    print('\t\tExporting final raster...')
    arcpy.management.CopyRaster(final_raster,
                                hydrography_raster,
                                '',
                                '',
                                '-32768',
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # Delete intermediate dataset
    if arcpy.Exists(flowline_raster) == 1:
        arcpy.management.Delete(flowline_raster)
    if arcpy.Exists(preliminary_raster) == 1:
        arcpy.management.Delete(preliminary_raster)
    if arcpy.Exists(flowline_buffered) == 1:
        arcpy.management.Delete(flowline_buffered)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully calculated hydrographic position.'
    return outprocess
