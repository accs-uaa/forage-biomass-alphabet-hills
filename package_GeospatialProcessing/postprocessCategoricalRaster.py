# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process categorical rasters
# Author: Timm Nawrocki
# Last Updated: 2023-02-22
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process categorical rasters" is a function that generalizes a predicted raster, applies a minimum mapping unit, and adds manually delineated classes.
# ---------------------------------------------------------------------------

# Define a function to post-process categorical raster
def postprocess_categorical_raster(**kwargs):
    """
    Description: generalizes categorical raster to minimum mapping unit and adds classes
    Inputs: 'minimum_count' -- the number of cells to be used as the minimum size for adjacent cells of a same value to be retained
            'water_value' -- integer value to use for water
            'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the predicted raster, the segments feature class, and the rivers raster
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires a predicted categorical raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import BoundaryClean
    from arcpy.sa import Con
    from arcpy.sa import ExtractByAttributes
    from arcpy.sa import MajorityFilter
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import RegionGroup
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Parse key word argument inputs
    minimum_count = kwargs['minimum_count']
    water_value = kwargs['water_value']
    null_statement = kwargs['null_statement']
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    river_raster = kwargs['input_array'][2]
    output_raster = kwargs['output_array'][0]

    # Define intermediate datasets
    work_folder = os.path.split(input_raster)[0]
    input_integer = os.path.join(work_folder, 'integer.tif')

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

    # Generalize raster results
    print(f'\tGeneralizing predicted raster...')
    iteration_start = time.time()
    # Copy raster to integer
    print('\t\tConverting input raster to integers...')
    arcpy.management.CopyRaster(input_raster,
                                input_integer,
                                '',
                                '',
                                '-128',
                                'NONE',
                                'NONE',
                                '8_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    arcpy.management.CalculateStatistics(input_integer)
    arcpy.management.BuildRasterAttributeTable(input_integer, 'Overwrite')
    # Clean raster boundaries
    print('\t\tCleaning raster boundaries...')
    raster_boundary = BoundaryClean(input_integer,
                                    'DESCEND',
                                    'TWO_WAY')
    # Apply majority filter
    print('\t\tSmoothing raster edges...')
    raster_majority = MajorityFilter(raster_boundary,
                                     'EIGHT',
                                     'MAJORITY')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate regions
    print(f'\tCalculating regions...')
    iteration_start = time.time()
    # Calculate regions
    print('\t\tCalculating contiguous value areas...')
    raster_regions = RegionGroup(raster_majority,
                                 'FOUR',
                                 'WITHIN',
                                 'NO_LINK',
                                 f'{water_value}')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Create nibble mask
    print(f'\tCreating mask raster of removed zones...')
    iteration_start = time.time()
    # Remove zones below minimum mapping unit
    print('\t\tRemoving contiguous areas below minimum mapping unit...')
    criteria = f'COUNT > {minimum_count}'
    raster_mask_1 = ExtractByAttributes(raster_regions,
                                        criteria)
    # Set null for selected values
    raster_mask_2 = SetNull(raster_majority, raster_mask_1, null_statement)
    # Set null for water
    raster_mask = SetNull(raster_mask_2 == 0, raster_mask_2)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Replace removed data
    print(f'\tReplacing removed data...')
    iteration_start = time.time()
    # Nibble raster
    raster_nibble = Nibble(raster_majority,
                           raster_mask,
                           'ALL_VALUES',
                           'PRESERVE_NODATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Add missing values for water
    print(f'\tAdding missing values...')
    iteration_start = time.time()
    # Add rivers
    raster_modified_1 = Con(Raster(river_raster) > 0, water_value, raster_nibble)
    # Add water
    raster_modified_2 = Con(raster_majority == water_value, water_value, raster_modified_1)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export final raster
    print(f'\tExporting final raster...')
    iteration_start = time.time()
    # Export extracted raster
    arcpy.management.CopyRaster(raster_modified_2,
                                output_raster,
                                '',
                                '',
                                '-128',
                                'NONE',
                                'NONE',
                                '8_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
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
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Delete intermediate datasets
    if arcpy.Exists(input_integer) == 1:
        arcpy.management.Delete(input_integer)

    # Return success message
    out_process = f'Successfully post-processed categorical raster.'
    return out_process
