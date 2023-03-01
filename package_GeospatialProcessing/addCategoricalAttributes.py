# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add categorical attributes
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add categorical attributes" is a function that builds a raster attribute table.
# ---------------------------------------------------------------------------

# Define a function to add categorical raster attributes
def add_categorical_attributes(**kwargs):
    """
    Description: adds attributes to each value in a categorical raster based on a dictionary
    Inputs: 'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the predicted raster, and the segments feature class
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires a predicted categorical raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import BoundaryClean
    from arcpy.sa import ExtractByAttributes
    from arcpy.sa import MajorityFilter
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import RegionGroup
    import datetime
    import os
    import time

    # Parse key word argument inputs
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
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

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Generalize raster results
    print(f'\tGeneralizing predicted raster...')
    iteration_start = time.time()
    # Copy raster to integer
    print('\t\tConverting input raster to integers...')
    arcpy.management.CopyRaster(input_raster,
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
    arcpy.management.CalculateStatistics(output_raster)
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

    # Return success message
    out_process = f'Successfully post-processed categorical raster.'
    return out_process
