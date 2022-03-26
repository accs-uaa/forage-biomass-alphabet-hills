# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert class data
# Author: Timm Nawrocki
# Last Updated: 2022-03-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Convert class data" is a function that converts class training data in a polygon feature class to a raster with predefined class values.
# ---------------------------------------------------------------------------

# Define a function to convert polygon class data to raster class data
def convert_class_data(**kwargs):
    """
    Description: converts class data in a polygon feature class to a raster of predefined values
    Inputs: 'statistic' -- a string value of the statistic to calculate
            'zone_field' -- a string value of the field to use from the zone raster to define zones
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster, the input raster, and the zone raster
            'output_array' -- an array containing the output summary raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input raster and zone raster from image segmentation that can be created through other scripts in this repository
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
    class_field = kwargs['class_field']
    value_dictionary = kwargs['value_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    class_feature = kwargs['input_array'][1]
    class_raster = kwargs['output_array'][0]

    # Define intermediate datasets
    temporary_feature = os.path.join(work_geodatabase, 'temporary_feature')
    initial_raster = os.path.join(os.path.split(class_raster)[0], 'initial_raster.tif')
    preliminary_raster = os.path.join(os.path.split(class_raster)[0], 'preliminary_raster.tif')

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

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Convert value dictionary to list
    class_list = list(value_dictionary)
    value_list = list(value_dictionary.values())
    class_first = class_list.pop(0)
    value_first = value_list.pop(0)

    # Create the first part of the code block
    code_head = f'def assign_values({class_field}):\n'

    # Create if statement
    if_statement = f'''    if {class_field} == "{class_first}":
        value = {value_first}\n'''

    # Create elif statement
    class_length = len(class_list)
    i = 0
    elif_statement = f''''''
    while i < class_length:
        add_statement = f'''    elif {class_field} == "{class_list[i]}":
        value = {value_list[i]}\n'''
        elif_statement = elif_statement + add_statement
        i += 1

    # Create else statement
    else_statement = f'''    else:
        value = 0
    return value'''

    # Create code block
    code_block = code_head + if_statement + elif_statement + else_statement

    # Create expression
    expression = f'assign_values(!{class_field}!)'

    # Add value field to feature class
    print(f'\tAdding values to polygon classes...')
    iteration_start = time.time()
    arcpy.management.CopyFeatures(class_feature, temporary_feature)
    arcpy.management.CalculateField(temporary_feature,
                                    'value',
                                    expression,
                                    'PYTHON3',
                                    code_block,
                                    'SHORT',
                                    'NO_ENFORCE_DOMAINS')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Convert to raster
    print(f'\tConvert feature class to raster...')
    iteration_start = time.time()
    # Convert features to raster
    arcpy.conversion.PolygonToRaster(temporary_feature,
                                     'value',
                                     initial_raster,
                                     'CELL_CENTER',
                                     '',
                                     cell_size,
                                     'BUILD')
    # Assign no data to zero
    value_raster = Con(IsNull(Raster(initial_raster)), 0, Raster(initial_raster))
    arcpy.management.CopyRaster(value_raster,
                                preliminary_raster,
                                '',
                                '',
                                '255',
                                'NONE',
                                'NONE',
                                '8_BIT_UNSIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # Extract raster to study area
    extract_raster = ExtractByMask(preliminary_raster, area_raster)
    arcpy.management.CopyRaster(extract_raster,
                                class_raster,
                                '',
                                '',
                                '255',
                                'NONE',
                                'NONE',
                                '8_BIT_UNSIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # Delete intermediate datasets
    if arcpy.Exists(temporary_feature) == 1:
        arcpy.management.Delete(temporary_feature)
    if arcpy.Exists(initial_raster) == 1:
        arcpy.management.Delete(initial_raster)
    if arcpy.Exists(preliminary_raster) == 1:
        arcpy.management.Delete(preliminary_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully created raster class data.'
    return outprocess
