# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Splice image segments to floodplains
# Author: Timm Nawrocki
# Last Updated: 2022-03-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Splice image segments to floodplains" is a function that splits image segments on divisions from a floodplain raster.
# ---------------------------------------------------------------------------

# Define a function to splice image segments and floodplain boundaries.
def splice_segments_floodplains(**kwargs):
    """
    Description: generates new features from the combined partitions of image segments and floodplain boundaries
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the original processed image segment polygons, and the floodplain boundary raster
            'output_array' -- an array containing the final segment raster, polygon feature class, and point feature class
    Returned Value: Returns a raster and feature classes on disk
    Preconditions: requires input image segments and floodplain boundary generated from other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import IsNull
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    segments_original = kwargs['input_array'][1]
    floodplain_raster = kwargs['input_array'][2]
    segments_raster = kwargs['output_array'][0]
    segments_final = kwargs['output_array'][1]
    segments_point = kwargs['output_array'][2]

    # Define intermediate dataset
    floodplain_feature = os.path.join(work_geodatabase, 'floodplain_polygon')
    segments_preliminary = os.path.join(work_geodatabase, 'segments_preliminary')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set initial cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Convert floodplain raster to polygon
    print('\tConverting floodplain raster to polygon...')
    iteration_start = time.time()
    value_raster = Con(IsNull(Raster(floodplain_raster)), 0, Raster(floodplain_raster))
    arcpy.conversion.RasterToPolygon(value_raster,
                                     floodplain_feature,
                                     'NO_SIMPLIFY',
                                     'VALUE',
                                     'SINGLE_OUTER_PART')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Splice polygons
    print('\tSplitting image segments using floodplain polygons...')
    iteration_start = time.time()
    arcpy.analysis.Intersect([segments_original, floodplain_feature],
                             segments_preliminary,
                             'ALL',
                             '',
                             'INPUT')
    # Split multi-part features
    print('\tSplitting multi-part features...')
    arcpy.management.MultipartToSinglepart(segments_preliminary, segments_final)
    # Convert final segments to point
    print('\t\tExporting point representation...')
    arcpy.management.FeatureToPoint(segments_final,
                                    segments_point,
                                    'INSIDE')
    # Convert final segments to raster
    print('\t\tExporting raster representation...')
    arcpy.conversion.PolygonToRaster(segments_final,
                                     'OBJECTID',
                                     segments_raster,
                                     'CELL_CENTER',
                                     '',
                                     2,
                                     'BUILD')
    # Delete intermediate dataset
    if arcpy.Exists(floodplain_feature) == 1:
        arcpy.management.Delete(floodplain_feature)
    if arcpy.Exists(segments_preliminary) == 1:
        arcpy.management.Delete(segments_preliminary)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully spliced image segments and floodplain boundaries.'
    return outprocess
