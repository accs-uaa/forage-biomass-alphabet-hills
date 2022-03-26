# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process image segments
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process image segments" is a function that converts an image segment raster exported from Google Earth Engine to a standard format raster with ordered positive values and creates a polygon and point representation.
# ---------------------------------------------------------------------------

# Define a function to convert image segments to standard raster, polygon, and point.
def postprocess_segments(**kwargs):
    """
    Description: converts image segments from Google Earth Engine to standard raster, polygon, and point representations.
    Inputs: 'cell_size' -- a cell size for the output raster
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the input raster
            'output_array' -- an array containing the output raster, polygon feature, and point feature
    Returned Value: Returns a raster and two feature classes to disk
    Preconditions: requires an image segment raster to be generated in and exported from Google Earth Engine
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    segments_initial = kwargs['input_array'][1]
    segments_final = kwargs['output_array'][0]
    segments_polygon = kwargs['output_array'][1]
    segments_point = kwargs['output_array'][2]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Define intermediate datasets
    polygon_initial = os.path.join(work_geodatabase, 'conversion_polygons')

    # Convert GEE output to formatted raster
    print(f'\tConverting raw segment raster to formatted segment raster...')
    iteration_start = time.time()
    # Convert initial image segments to polygon
    extract_raster = ExtractByMask(segments_initial, area_raster)
    arcpy.conversion.RasterToPolygon(extract_raster,
                                     polygon_initial,
                                     'NO_SIMPLIFY',
                                     'VALUE',
                                     'SINGLE_OUTER_PART',
                                     '')
    # Convert initial polygon to raster
    arcpy.conversion.PolygonToRaster(polygon_initial,
                                     'OBJECTID',
                                     segments_final,
                                     'CELL_CENTER',
                                     '',
                                     cell_size,
                                     'BUILD'
                                     )
    # Remove intermediate polygons
    arcpy.management.Delete(polygon_initial)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Create vector representations
    print(f'\tCreating polygon and point representations of segments...')
    iteration_start = time.time()
    # Convert final segments to polygon
    arcpy.conversion.RasterToPolygon(segments_final,
                                     segments_polygon,
                                     'NO_SIMPLIFY',
                                     'VALUE',
                                     'SINGLE_OUTER_PART',
                                     '')
    # Convert final segments to points
    arcpy.management.FeatureToPoint(segments_polygon,
                                    segments_point,
                                    'INSIDE')
    # Add xy coordinates to points
    arcpy.management.AddXY(segments_point)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    out_process = f'Successfully created image segment raster and vectors.'
    return out_process
