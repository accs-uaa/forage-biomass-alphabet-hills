# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Sampling Block
# Author: Timm Nawrocki
# Last Updated: 2021-06-23
# Usage: Must be executed in an ArcGIS Pro Python 3.6+ installation.
# Description: "Create Sampling Block" is a function that generates a sample block using a buffer and an optional erase feature class.
# ---------------------------------------------------------------------------

# Define a function to generate a sampling block from a point or polygon
def create_sample_block(**kwargs):
    """
    Description: buffers a point or polygon to form a sampling block with an optional erase feature class
    Inputs: 'buffer_distance' -- the distance to buffer the initial point or polygon, which represents the maximum possible walking distance
            'subdivide_number' -- the number of subdivisions to create per block
            'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the starting feature class (must be a point or polygon and must be listed first) and an optional feature class used to erase area from the sample block (such as a lakes feature class)
            'output_array' -- an array containing the output polygon feature class
    Returned Value: Returns a polygon feature class containing the sampling block polygon
    Preconditions: requires a manually selected starting unit and a manually generated erase feature class (optional)
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    buffer_distance = kwargs['buffer_distance']
    subdivide_number = kwargs['subdivide_number']
    work_geodatabase = kwargs['work_geodatabase']
    inputs = kwargs['input_array']
    unit_feature = inputs.pop(0)
    output_feature = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Define intermediate datasets
    buffer_feature = os.path.join(work_geodatabase, 'buffer_feature')

    # Start timing function
    iteration_start = time.time()
    print(f'\tBuffer starting unit by {buffer_distance}...')
    # Determine if erase feature supplied
    if len(inputs) > 0:
        # Define erase feature
        erase_feature = inputs[0]
        # Buffer initial unit
        arcpy.analysis.PairwiseBuffer(unit_feature,
                                      buffer_feature,
                                      buffer_distance,
                                      'NONE',
                                      '',
                                      'PLANAR'
                                      )
        # Erase the erase feature from the buffer feature
        arcpy.analysis.PairwiseErase(buffer_feature,
                                     erase_feature,
                                     output_feature,
                                     '')
    # If no erase feature was supplied then conduct the buffer without the erase step
    else:
        # Buffer initial unit
        arcpy.analysis.PairwiseBuffer(unit_feature,
                                      output_feature,
                                      buffer_distance,
                                      'NONE',
                                      '',
                                      'PLANAR'
                                      )
    # Delete non-required fields
    for field in arcpy.ListFields(output_feature):
        if (field.type != 'OID'
                and field.type != 'Geometry'
                and field.name != 'Shape_Length'
                and field.name != 'Shape_Area'):
            arcpy.management.DeleteField(output_feature, field.name)
    # Add field with block name
    arcpy.management.AddField(output_feature,
                              'block',
                              'TEXT')
    block_name = os.path.split(output_feature)[1]
    expression = f'"{block_name}"'
    code_block = ''
    arcpy.management.CalculateField(output_feature,
                                    'block',
                                    expression,
                                    'PYTHON3',
                                    code_block)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Subdivide block if subdivide number is greater than 1
    if subdivide_number > 1:
        # Start timing function
        iteration_start = time.time()
        print(f'\tSubdividing sampling block...')
        # Subdivide sampling block based on user-supplied number
        block_subdivisions = output_feature + f'_subdivisions'
        arcpy.management.SubdividePolygon(output_feature,
                                          block_subdivisions,
                                          'NUMBER_OF_EQUAL_PARTS',
                                          subdivide_number,
                                          '',
                                          '',
                                          0,
                                          'STACKED_BLOCKS')
        # Iterate through subdivisions and export each as separate feature class
        count = 1
        with arcpy.da.SearchCursor(block_subdivisions, 'SHAPE@') as cursor:
            for row in cursor:
                # Define output feature class
                output_subdivision = output_feature + f'_{str(count)}'
                # Copy feature to output feature class
                arcpy.management.CopyFeatures(row[0],
                                              output_subdivision)
                # Add field with unit name
                arcpy.management.AddField(output_subdivision,
                                          'unit',
                                          'TEXT')
                unit_name = os.path.split(output_subdivision)[1]
                expression = f'"{unit_name}"'
                code_block = ''
                arcpy.management.CalculateField(output_subdivision,
                                                'unit',
                                                expression,
                                                'PYTHON3',
                                                code_block)
                count += 1
    else:
        print('\tNumber of subdivisions equals one.')
    # Delete the intermediate dataset if it exists
    if arcpy.Exists(buffer_feature) == 1:
        arcpy.management.Delete(buffer_feature)
    if arcpy.Exists(block_subdivisions) == 1:
        arcpy.management.Delete(block_subdivisions)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = 'Successfully created block feature class.'
    return out_process
