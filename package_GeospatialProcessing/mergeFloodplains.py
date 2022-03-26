# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge floodplains
# Author: Timm Nawrocki
# Last Updated: 2022-03-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Merge floodplains" is a function that calculates floodplains from a one or more flowline position rasters.
# ---------------------------------------------------------------------------

# Define a function to generate floodplains.
def merge_floodplains(**kwargs):
    """
    Description: generates floodplains from a float elevation raster and a set of flowlines
    Inputs: 'thresholds' -- one threshold per flowline feature class included in the floodplain calculate, where each threshold is the upper bound of the floodplain
            'area_limit' -- an integer value representing the maximum size of excluded polygon to convert to floodplain
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the flowline feature classes (one per threshold), and the flowline position rasters (one per threshold)
            'output_array' -- an array containing the floodplain position raster and smoothed feature class
    Returned Value: Returns a raster on disk
    Preconditions: requires input flowlines and position rasters that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import CellStatistics
    from arcpy.sa import Con
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    thresholds = kwargs['thresholds']
    area_limit = kwargs['area_limit']
    work_geodatabase = kwargs['work_geodatabase']
    input_datasets = kwargs['input_array']
    area_raster = input_datasets.pop(0)
    floodplain_raster = kwargs['output_array'][0]
    floodplain_feature = kwargs['output_array'][1]

    # Parse flowlines and position rasters
    number = len(thresholds)
    upper_position = (number * 2) + 1
    flowlines = input_datasets[0:number]
    positions = input_datasets[number:upper_position]

    # Define intermediate dataset
    hydrography_folder = os.path.split(floodplain_raster)[0]
    preliminary_raster = os.path.join(hydrography_folder, 'Preliminary.tif')
    simple_feature = os.path.join(work_geodatabase, 'floodplain_simple')
    remove_feature = os.path.join(work_geodatabase, 'floodplain_only')
    dissolve_feature = os.path.join(work_geodatabase, 'floodplain_dissolve')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set initial cell size environment
    cell_size = arcpy.management.GetRasterProperties(positions[0], 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Merge flowlines if there is more than one flowline feature class
    if len(flowlines) > 1:
        # Define intermediate flowline dataset
        flowline_feature = os.path.join(work_geodatabase, 'Alphabet_Flowlines')
        # Merge feature classes
        arcpy.management.Merge(flowlines, flowline_feature)
    else:
        flowline_feature = flowlines[0]

    # Convert position to binary floodplain for each position raster
    count = 1
    raster_list = []
    for threshold in thresholds:
        print(f'\tConverting position raster {count} of {number}...')
        iteration_start = time.time()
        # Set identifier
        idn = count - 1
        # Convert continuous raster to binary based on threshold
        convert_raster = Con(positions[idn], 1, 0, f'VALUE <= {threshold}')
        # Append converted raster to list
        raster_list.append(convert_raster)
        count += 1
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

    # Add binary position rasters and correct values
    if number > 1:
        print(f'\tCalculating binary position sum...')
        iteration_start = time.time()
        # Add binary position rasters
        sum_raster = CellStatistics(raster_list, 'SUM', 'DATA', 'SINGLE_BAND')
        # Correct raster overlap
        corrected_raster = Con(sum_raster, 1, 0, 'VALUE > 0')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        corrected_raster = raster_list[0]

    # Export preliminary raster
    print('\tExporting preliminary floodplain raster...')
    iteration_start = time.time()
    arcpy.management.CopyRaster(corrected_raster,
                                preliminary_raster,
                                '',
                                '',
                                '3',
                                'NONE',
                                'NONE',
                                '2_BIT',
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
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Convert floodplain raster to feature
    print('\tConverting floodplain raster to feature...')
    iteration_start = time.time()
    # Convert raster to polygon
    print('\t\tConverting raster to polygon...')
    arcpy.conversion.RasterToPolygon(preliminary_raster,
                                     simple_feature,
                                     'SIMPLIFY',
                                     'VALUE',
                                     'SINGLE_OUTER_PART')
    # Convert exclusion polygons to floodplain
    print('\t\tCorrecting floodplain exclusions...')
    code_block = f'''def floodplain_assign(gridcode, area):
    if gridcode == 1:
        value = 1
    elif gridcode == 0 and area < {area_limit}:
        value = 1
    else:
        value = 0
    return value'''
    arcpy.management.CalculateField(simple_feature,
                                    'gridcode',
                                    'floodplain_assign(!gridcode!, !Shape_Area!)',
                                    'PYTHON3',
                                    code_block)
    # Remove non-floodplain polygons
    print('\t\tRemoving non-floodplain polygons...')
    simple_layer = 'simple_layer'
    arcpy.management.MakeFeatureLayer(simple_feature,
                                      simple_layer)
    arcpy.management.SelectLayerByAttribute(simple_layer,
                                            'NEW_SELECTION',
                                            'gridcode = 0',
                                            'NON_INVERT')
    arcpy.management.DeleteFeatures(simple_layer)
    arcpy.analysis.PairwiseDissolve(simple_layer,
                                    remove_feature,
                                    'gridcode',
                                    '',
                                    'SINGLE_PART')
    # Remove floodplain polygons that do not intersect flowlines
    print('\t\tRemoving floodplain polygons that do not intersect flowlines...')
    remove_layer = 'remove_layer'
    arcpy.management.MakeFeatureLayer(remove_feature,
                                      remove_layer)
    arcpy.management.SelectLayerByLocation(remove_layer,
                                           'INTERSECT',
                                           flowline_feature,
                                           '',
                                           'NEW_SELECTION',
                                           'INVERT')
    arcpy.management.DeleteFeatures(remove_layer)
    arcpy.cartography.SmoothPolygon(remove_layer,
                                    floodplain_feature,
                                    'PAEK',
                                    20)
    # Update cell size environment
    cell_size_2m = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size_2m)
    # Convert floodplain polygon to raster
    print('\t\tConverting floodplain polygon to final raster...')
    arcpy.analysis.PairwiseDissolve(floodplain_feature,
                                    dissolve_feature,
                                    '',
                                    '',
                                    'MULTI_PART')
    arcpy.conversion.PolygonToRaster(dissolve_feature,
                                     'OBJECTID',
                                     floodplain_raster,
                                     'CELL_CENTER',
                                     '',
                                     '',
                                     'BUILD')
    # Delete intermediate dataset
    if arcpy.Exists(preliminary_raster) == 1:
        arcpy.management.Delete(preliminary_raster)
    if arcpy.Exists(simple_feature) == 1:
        arcpy.management.Delete(simple_feature)
    if arcpy.Exists(remove_feature) == 1:
        arcpy.management.Delete(remove_feature)
    if arcpy.Exists(simple_layer) == 1:
        arcpy.management.Delete(simple_layer)
    if arcpy.Exists(remove_layer) == 1:
        arcpy.management.Delete(remove_layer)
    if number > 1 and arcpy.Exists(flowline_feature) == 1:
        arcpy.management.Delete(flowline_feature)
    if arcpy.Exists(dissolve_feature) == 1:
        arcpy.management.Delete(dissolve_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully calculated boundaries.'
    return outprocess
