# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse image segments
# Author: Timm Nawrocki
# Last Updated: 2022-03-26
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Parse image segments" is a function that extracts the image segments that overlap a validation grid.
# ---------------------------------------------------------------------------

# Define a function to parse image segments for a grid index
def parse_image_segments(**kwargs):
    """
    Description: extracts the image segments that overlap a selected grid
    Inputs: 'tile_name' -- a field name in the grid index that stores the tile name
            'work_geodatabase' -- a geodatabase to store results
            'input_array' -- an array containing the study area raster, the input grid index, the input image segment points, and the input image segment polygons
            'output_folder' -- an empty folder to store the parsed image segment rasters
    Returned Value: Returns a raster dataset for each grid in grid index
    Preconditions: grid index must have been generated using create_grid_indices
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    tile_name = kwargs['tile_name']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    grid_index = kwargs['input_array'][1]
    segments_point = kwargs['input_array'][2]
    segments_polygon = kwargs['input_array'][3]
    output_folder = kwargs['output_folder']

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set the snap raster
    arcpy.env.snapRaster = area_raster

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Print initial status
    print(f'Extracting grid tiles from {os.path.split(grid_index)[1]}...')

    # Define fields for search cursor
    fields = ['SHAPE@', tile_name]
    # Initiate search cursor on grid index with defined fields
    with arcpy.da.SearchCursor(grid_index, fields) as cursor:
        # Iterate through each feature in the feature class
        for row in cursor:
            # Define output datasets
            output_points = os.path.join(work_geodatabase, 'points_' + row[1])
            output_polygons = os.path.join(work_geodatabase, 'polygons_' + row[1])
            output_grid = os.path.join(output_folder, row[1] + '.tif')

            # Define layers
            point_layer = 'point_layer'
            polygon_layer = 'polygon_layer'

            # Set initial extent
            arcpy.env.extent = Raster(area_raster).extent

            # If tile does not exist, then create tile
            if arcpy.Exists(output_grid) == 0:
                print(f'\tProcessing grid tile {os.path.split(output_grid)[1]}...')
                iteration_start = time.time()
                # Delete feature classes if they exist
                if arcpy.Exists(output_points) == 1:
                    arcpy.management.Delete(output_points)
                if arcpy.Exists(output_polygons) == 1:
                    arcpy.management.Delete(output_polygons)
                # Make segment point layer
                arcpy.management.MakeFeatureLayer(segments_point, point_layer)
                # Select points by overlap with grid
                arcpy.management.SelectLayerByLocation(point_layer,
                                                       'INTERSECT',
                                                       row[0],
                                                       '',
                                                       'NEW_SELECTION',
                                                       'NOT_INVERT')
                # Copy selected points to new feature class and remove unnecessary fields
                arcpy.management.CopyFeatures(point_layer, output_points)
                point_field_list = arcpy.ListFields(output_points)
                drop_point_fields = []
                for field in point_field_list:
                    if not field.required:
                        drop_point_fields.append(field.name)
                arcpy.management.DeleteField(output_points, drop_point_fields)
                arcpy.management.CalculateField(output_points,
                                                'segment_id',
                                                '!OBJECTID!',
                                                'PYTHON3',
                                                '',
                                                'LONG',
                                                'NO_ENFORCE_DOMAINS')
                # Make segment polygon layer
                arcpy.management.MakeFeatureLayer(segments_polygon, polygon_layer)
                # Select polygons by overlap with points
                arcpy.management.SelectLayerByLocation(polygon_layer,
                                                       'INTERSECT',
                                                       output_points,
                                                       '',
                                                       'NEW_SELECTION',
                                                       'NOT_INVERT')
                # Copy selected points to new feature class and remove unnecessary fields
                arcpy.management.CopyFeatures(polygon_layer, output_polygons)
                polygon_field_list = arcpy.ListFields(output_polygons)
                drop_polygon_fields = []
                for field in polygon_field_list:
                    if not field.required:
                        drop_polygon_fields.append(field.name)
                arcpy.management.DeleteField(output_polygons, drop_polygon_fields)
                arcpy.management.CalculateField(output_polygons,
                                                'segment_id',
                                                '!OBJECTID!',
                                                'PYTHON3',
                                                '',
                                                'LONG',
                                                'NO_ENFORCE_DOMAINS')
                # Update extent
                desc = arcpy.Describe(output_polygons)
                xmin = desc.extent.XMin
                xmax = desc.extent.XMax
                ymin = desc.extent.YMin
                ymax = desc.extent.YMax
                arcpy.env.extent = arcpy.Extent(xmin, ymin, xmax, ymax)
                # Copy features to raster
                arcpy.conversion.PolygonToRaster(output_polygons,
                                                 'OBJECTID',
                                                 output_grid,
                                                 'CELL_CENTER',
                                                 '',
                                                 cell_size,
                                                 'BUILD')
                # Add XY coordinates to points
                arcpy.management.AddXY(output_points)
                # End timing
                iteration_end = time.time()
                iteration_elapsed = int(iteration_end - iteration_start)
                iteration_success_time = datetime.datetime.now()
                # Report success
                print(f'\tOutput grid {os.path.split(output_grid)[1]} completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            else:
                print(f'\tOutput grid {os.path.split(output_grid)[1]} already exists...')
                print('\t----------')

    # Return final status
    out_process = 'Finished parsing segments to grids.'
    return out_process
