# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate hydrographic position
# Author: Timm Nawrocki
# Last Updated: 2022-01-16
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Generate hydrographic position" is a function that calculates floodplains from a float elevation raster and a set of flowlines, which can be derived from a DEM, the NHD, or manual delineation (or some combination thereof).
# ---------------------------------------------------------------------------

# Define a function to generate floodplains.
def generate_hydrographic_position(**kwargs):
    """
    Description: generates floodplains from a float elevation raster and a set of flowlines
    Inputs: 'threshold' -- a threshold value for floodplain determination
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the float elevation raster (must be second), and the flowlines (must be third)
            'output_array' -- an array containing the floodplain feature class and floodplain raster
    Returned Value: Returns a feature class and raster on disk
    Preconditions: requires input elevation and flowlines that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    position_width = kwargs['position_width']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    elevation_raster = kwargs['input_array'][1]
    flowline_feature = kwargs['input_array'][2]
    hydrography_raster = kwargs['output_array'][0]


    # Define intermediate dataset
    hydrography_folder = os.path.split(hydrography_raster)[0]
    flowline_raster = os.path.join(hydrography_folder, 'Flowlines.tif')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(elevation_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Calculate landscape position
    print('\tCalculating landscape position...')
    iteration_start = time.time()
    # Determine neighborhood size
    axis_length = int(position_width / float(cell_size))
    # Define a neighborhood variable
    neighborhood = NbrRectangle(axis_length, axis_length, 'CELL')
    # Calculate focal mean
    print('\t\tCalculating focal mean...')
    focal_mean = FocalStatistics(elevation_raster, neighborhood, 'MEAN', 'DATA')
    # Calculate topographic position
    print('\t\tCalculating topographic position...')
    position_raster = Raster(elevation_raster) - focal_mean
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Extract position to flowlines
    print('\tCalculating flowline position...')
    iteration_start = time.time()
    # Convert stream network to raster
    print('\t\tConverting stream network to raster...')
    arcpy.conversion.PolylineToRaster(flowline_feature,
                                      'grid_code',
                                      flowline_raster,
                                      'MAXIMUM_LENGTH',
                                      '',
                                      cell_size,
                                      'BUILD')
    # Extract elevation to stream network
    print('\t\tExtracting elevation to stream network...')
    position_extract = ExtractByMask(position_raster, Raster(flowline_raster))
    # Expand stream elevation
    print('\t\tExpanding stream position...')
    flowline_position = Nibble(position_extract, Raster(flowline_raster), 'DATA_ONLY', 'PROCESS_NODATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate hydrographic position
    print('\tSubtracting flowline and landscape positions...')
    iteration_start = time.time()
    hydrographic_position = (position_raster - flowline_position)**2
    integer_raster = Int((hydrographic_position * 100) + 0.5)
    arcpy.management.CopyRaster(integer_raster,
                                hydrography_raster,
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
    # Delete intermediate dataset
    if arcpy.Exists(flowline_raster) == 1:
        arcpy.management.Delete(flowline_raster)
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
