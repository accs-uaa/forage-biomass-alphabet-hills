# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert validation grid
# Author: Timm Nawrocki
# Last Updated: 2021-11-03
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Convert validation grid" is a function that converts a validation grid to a validation group raster for a study area boundary.
# ---------------------------------------------------------------------------

# Define function to convert validation grid
def convert_validation_grid(**kwargs):
    """
    Description: converts a validation grid to a validation group raster within a study area
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the validation grid feature class, the study area feature class, and the study area raster
            'output_array' -- an array containing the output validation raster
    Returned Value: Returns raster of validation groups
    Preconditions: validation grid must be created using create grid index function
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    validation_feature = kwargs['input_array'][0]
    area_feature = kwargs['input_array'][1]
    area_raster = kwargs['input_array'][2]
    validation_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Create intermediate datasets
    validation_clip = os.path.join(work_geodatabase, 'validation_clip')

    # Clip validation grid to study area feature class
    print(f'\tClipping validation grid index...')
    iteration_start = time.time()
    arcpy.analysis.PairwiseClip(validation_feature,
                                area_feature,
                                validation_clip)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Convert clipped validation grid to raster
    print(f'\tConverting validation grid to raster...')
    iteration_start = time.time()
    arcpy.conversion.PolygonToRaster(validation_clip,
                                     'OBJECTID',
                                     validation_raster,
                                     'CELL_CENTER',
                                     '',
                                     cell_size,
                                     'BUILD')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Remove intermediate datasets
    arcpy.management.Delete(validation_clip)

    # Return success message
    outprocess = 'Successfully created validation raster.'
    return outprocess
