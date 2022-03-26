# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Probabilistic Site Selection
# Author: Timm Nawrocki
# Last Updated: 2021-06-23
# Usage: Must be executed in an ArcGIS Pro Python 3.6+ installation.
# Description: "Probabilistic Site Selection" is a function that generates a random selection of sample sites according to a continuous probability raster so that the resulting points are spatially balanced.
# ---------------------------------------------------------------------------

# Define a function to generate spatially balanced points from a continuous raster
def probabilistic_site_selection(**kwargs):
    """
    Description: generates random set of spatially balanced points based on a spatial probability distribution
    Inputs: 'number_points' -- the number of points to generate
            'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the study area raster (must be first), the continuous raster from which to generate selection probabilities (must be second), and a sampling block polygon feature class (must be last)
            'output_array' -- an array containing the output point feature class
    Returned Value: Returns a point feature class containing spatially balanced sampling sites
    Preconditions: requires an existing continuous raster dataset from which to generate the spatial probability distribution and a sampling block polygon
    """

    # Import packages
    import arcpy
    from arcpy.ga import CreateSpatiallyBalancedPoints
    from arcpy.sa import ExtractByMask
    from arcpy.sa import ExtractValuesToPoints
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    number_points = kwargs['number_points']
    work_geodatabase = kwargs['work_geodatabase']
    study_area = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    block_polygon = kwargs['input_array'][2]
    output_points = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set snap raster, extent, and cell size
    arcpy.env.snapRaster = study_area
    arcpy.env.extent = Raster(study_area).extent
    arcpy.env.cellSize = "MINOF"

    # Set random seed
    arcpy.env.randomGenerator = '314 ACM599'

    # Define intermediate datasets
    intermediate_points = os.path.join(work_geodatabase, 'intermediate_points')
    extract_points = os.path.join(work_geodatabase, 'extract_points')

    # Start timing function
    iteration_start = time.time()
    print(f'\tExtracting raster to block...')
    # Extract raster to block
    extract_raster = ExtractByMask(input_raster, block_polygon)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    print(f'\tConverting continuous raster to spatial probability distribution...')
    # convert raster to probability distribution
    maximum_value = int(arcpy.management.GetRasterProperties(extract_raster, 'MAXIMUM').getOutput(0))
    probability_raster = (extract_raster + 1) / (maximum_value + 1)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    print(f'\tCreating spatially balanced points...')
    # Create spatially balanced points
    CreateSpatiallyBalancedPoints(probability_raster,
                                  number_points,
                                  intermediate_points)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    print(f'\tExtracting raster values to points...')
    # Extract raster values to points
    ExtractValuesToPoints(intermediate_points,
                          extract_raster,
                          extract_points,
                          'NONE',
                          'VALUE_ONLY'
                          )
    # Project points to NAD83
    input_system = arcpy.SpatialReference(3338)
    output_system = arcpy.SpatialReference(4269)
    arcpy.management.Project(extract_points,
                             output_points,
                             output_system,
                             '',
                             input_system,
                             'NO_PRESERVE_SHAPE',
                             '',
                             'NO_VERTICAL')
    # Add field with site code
    arcpy.management.AddField(output_points,
                              'site_code',
                              'TEXT')
    block_name = os.path.split(block_polygon)[1]
    block_number = block_name.replace('Block_', '')
    block_prefix = block_number.replace('_', '')
    expression = f'assign_code({block_prefix}, !OBJECTID!)'
    code_block = '''def assign_code(block_prefix, objectid):
        if objectid < 10:
            site_code = str(block_prefix) + "0" + str(objectid)
        else:
            site_code = str(block_prefix) + str(objectid)
        return site_code'''
    arcpy.management.CalculateField(output_points,
                                    'site_code',
                                    expression,
                                    'PYTHON3',
                                    code_block)
    # Add latitude and longitude in decimal degrees
    arcpy.management.AddXY(output_points)
    # Delete intermediate datasets
    if arcpy.Exists(intermediate_points) == 1:
        arcpy.management.Delete(intermediate_points)
    if arcpy.Exists(extract_points) == 1:
        arcpy.management.Delete(extract_points)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = 'Successfully created spatially balanced points.'
    return out_process
