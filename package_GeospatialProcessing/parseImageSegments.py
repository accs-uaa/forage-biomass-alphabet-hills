# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse image segments
# Author: Timm Nawrocki
# Last Updated: 2022-03-22
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Parse image segments" is a function that extracts the image segments that overlap a validation grid.
# ---------------------------------------------------------------------------

# Define a function to parse image segments for a grid index
def parse_image_segments(**kwargs):
    """
    Description: extracts the image segments that overlap a selected grid
    Inputs: 'tile_name' -- a field name in the grid index that stores the tile name
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the study area raster, the input grid index, and the input image segments
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
    segments_feature = kwargs['input_array'][2]
    output_folder = kwargs['output_folder']

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '75%'

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
            # Define intermediate and output datasets
            temporary_segments = os.path.join(arcpy.env.workspace, 'Grid_' + row[1] + '_Selected')
            output_grid = os.path.join(output_folder, row[1] + '.tif')

            # Set initial extent
            arcpy.env.extent = Raster(area_raster).extent

            # Define segments layer
            segments_layer = 'segments_layer'

            # If tile does not exist, then create tile
            if arcpy.Exists(output_grid) == 0:
                print(f'\tProcessing grid tile {os.path.split(output_grid)[1]}...')
                iteration_start = time.time()
                # Make segments layer
                arcpy.management.MakeFeatureLayer(segments_feature, segments_layer)
                # Select segments by overlap with grid
                arcpy.management.SelectLayerByLocation(segments_layer,
                                                       'INTERSECT',
                                                       row[0],
                                                       '',
                                                       'NEW_SELECTION',
                                                       'NOT_INVERT')
                # Copy selected segments to new feature class
                arcpy.management.CopyFeatures(segments_layer, temporary_segments)
                # Update extent
                desc = arcpy.Describe(temporary_segments)
                xmin = desc.extent.XMin
                xmax = desc.extent.XMax
                ymin = desc.extent.YMin
                ymax = desc.extent.YMax
                arcpy.env.extent = arcpy.Extent(xmin, ymin, xmax, ymax)
                # Copy features to raster
                arcpy.conversion.PolygonToRaster(temporary_segments,
                                                 'OBJECTID',
                                                 output_grid,
                                                 'CELL_CENTER',
                                                 '',
                                                 cell_size,
                                                 'BUILD')
                # If temporary feature class exists, then delete it
                if arcpy.Exists(temporary_segments) == 1:
                    arcpy.management.Delete(temporary_segments)
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
    out_process = 'Completed creation of grid tiles.'
    return out_process
