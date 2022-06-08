# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert predictions to raster
# Author: Timm Nawrocki
# Last Updated: 2022-06-07
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Convert predictions to raster" is a function that joins attributes from a csv file to a raster layer and exports as a new raster.
# ---------------------------------------------------------------------------

# Define a function to join attributes to a raster by value
def predictions_to_raster(**kwargs):
    """
    Description: joins attributes to a raster by value
    Inputs: 'segment_folder' -- a folder containing gridded image segments
            'prediction_folder' -- a folder containing the predicted class tables
            'grid_folder' -- a folder to store the gridded raster outputs
            'target_field' -- a field containing the data to convert to raster values
            'data_type' -- specify either 'continuous' or 'discrete'
            'attribute_dictionary' -- a dictionary to use in building the attribute table for discrete data
            'conversion_factor' -- a number to multiply continuous data by to form integer output
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster, the input raster, and the attribute table
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input raster and an predicted table that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import ZonalStatistics
    import datetime
    import glob
    import os
    import time

    # Parse key word argument inputs
    segment_folder = kwargs['segment_folder']
    prediction_folder = kwargs['prediction_folder']
    grid_folder = kwargs['grid_folder']
    target_field = kwargs['target_field']
    data_type = kwargs['data_type']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set output coordinate system
    arcpy.env.outputCoordinateSystem = Raster(area_raster)
    spatial_reference = arcpy.Describe(area_raster).spatialReference

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Calculate buffer distance
    buffer_distance = (int(cell_size) * 1.42) / 2

    # Assign bit depth and no data value
    if data_type == 'discrete':
        bit_depth = '8_BIT_SIGNED'
        no_data_value = '-128'
    else:
        bit_depth = '16_BIT_SIGNED'
        no_data_value = '-32768'

    # Generate list of predictions
    os.chdir(prediction_folder)
    input_files = glob.glob('*.csv')

    # Create empty list of rasters
    grid_rasters = []

    # Convert each prediction to raster
    count = 1
    input_length = len(input_files)
    for file in input_files:
        # Define grid name
        grid = os.path.splitext(file)[0]

        # Define input file
        input_file = os.path.join(prediction_folder, file)

        # Define input datasets
        segment_raster = os.path.join(segment_folder, grid + '.tif')

        # Define intermediate datasets
        point_feature = os.path.join(work_geodatabase, 'Predictions_' + grid)
        polygon_feature = os.path.join(work_geodatabase, 'Predictions_Buffer_' + grid)
        point_raster = os.path.join(grid_folder, grid + '_Point.tif')
        output_grid = os.path.join(grid_folder, grid + '.tif')

        # Create output grid if it does not already exist
        if arcpy.Exists(output_grid) == 0:
            print(f'\tConverting raster {count} of {input_length}...')
            iteration_start = time.time()
            # Convert table to points
            arcpy.management.XYTableToPoint(input_file,
                                            point_feature,
                                            'POINT_X',
                                            'POINT_Y',
                                            '',
                                            spatial_reference)
            # Buffer points by buffer distance
            arcpy.analysis.PairwiseBuffer(point_feature,
                                          polygon_feature,
                                          f'{buffer_distance} METERS',
                                          'NONE',
                                          '',
                                          'PLANAR')
            # Convert polygon to raster
            arcpy.conversion.PolygonToRaster(polygon_feature,
                                             target_field,
                                             point_raster,
                                             'CELL_CENTER',
                                             '',
                                             cell_size,
                                             'BUILD')
            # Calculate zonal majority from point raster
            if data_type == 'discrete':
                full_raster = ZonalStatistics(segment_raster,
                                              'VALUE',
                                              point_raster,
                                              'MAJORITY',
                                              'DATA',
                                              'CURRENT_SLICE')
            else:
                conversion_factor = kwargs['conversion_factor']
                adjust_raster = Int(Raster(point_raster) * conversion_factor)
                full_raster = ZonalStatistics(segment_raster,
                                              'VALUE',
                                              adjust_raster,
                                              'MAJORITY',
                                              'DATA',
                                              'CURRENT_SLICE')
            # Enforce integers on output
            integer_raster = Int(full_raster)
            # Export output raster
            arcpy.management.CopyRaster(integer_raster,
                                        output_grid,
                                        '',
                                        '',
                                        no_data_value,
                                        'NONE',
                                        'NONE',
                                        bit_depth,
                                        'NONE',
                                        'NONE',
                                        'TIFF',
                                        'NONE',
                                        'CURRENT_SLICE',
                                        'NO_TRANSPOSE')
            # Delete intermediate datasets
            if arcpy.Exists(point_feature) == 1:
                arcpy.management.Delete(point_feature)
            if arcpy.Exists(polygon_feature) == 1:
                arcpy.management.Delete(polygon_feature)
            if arcpy.Exists(point_raster) == 1:
                arcpy.management.Delete(point_raster)
            # End timing
            iteration_end = time.time()
            iteration_elapsed = int(iteration_end - iteration_start)
            iteration_success_time = datetime.datetime.now()
            # Report success
            print(
                f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        else:
            print(f'\tRaster {count} of {input_length} already exists.')
        # Append raster to list
        grid_rasters.append(output_grid)
        print('\t----------')
        # Increase count
        count += 1

    # Define attribute table
    attribute_dictionary = kwargs['attribute_dictionary']
    # Mosaic rasters to output
    grid_number = len(grid_rasters)
    print(f'Merging {grid_number} grid rasters into final output...')
    iteration_start = time.time()
    output_folder, output_name = os.path.split(output_raster)
    arcpy.management.MosaicToNewRaster(grid_rasters,
                                       output_folder,
                                       output_name,
                                       spatial_reference,
                                       bit_depth,
                                       cell_size,
                                       '1',
                                       'FIRST',
                                       'FIRST')
    # If data type is discrete, then assign attributes
    if data_type == 'discrete':
        # Create raster attribute table
        arcpy.management.BuildRasterAttributeTable(output_raster, 'Overwrite')
        # Calculate attribute label field
        code_block = '''def get_label(value, dictionary):
    for label, id in dictionary.items():
        if value == id:
            return label'''
        expression = f'get_label(!VALUE!, {attribute_dictionary})'
        arcpy.management.CalculateField(output_raster,
                                        'label',
                                        expression,
                                        'PYTHON3',
                                        code_block)
    else:
        # Create raster attribute table
        arcpy.management.BuildRasterAttributeTable(output_raster, 'Overwrite')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Return final status
    out_process = 'Finished converting predictions to raster.'
    return out_process
