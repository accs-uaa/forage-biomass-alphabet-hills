# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process continuous rasters
# Author: Timm Nawrocki
# Last Updated: 2023-03-06
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process continuous rasters" is a function that corrects a continuous raster or set of rasters based on values from a categorical raster.
# ---------------------------------------------------------------------------

# Define a function to post-process continuous raster
def postprocess_continuous_raster(**kwargs):
    """
    Description: corrects continuous raster based on values of categorical raster
    Inputs: 'calculate_mean' -- either True or False
            'conditional_statement' -- a statement of values to select from the categorical raster to set the continuous raster to 0
            'data_type' -- data type for the output raster using arcpy naming conventions
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the categorical raster (must be second), the river raster (must be third), and the raster or rasters (if calculate_mean is True) to post-process
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires one or more predicted continuous rasters
    """

    # Import packages
    import arcpy
    from arcpy.sa import CellStatistics
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import IsNull
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    calculate_mean = kwargs['calculate_mean']
    conditional_statement = kwargs['conditional_statement']
    data_type = kwargs['data_type']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'].pop(0)
    categorical_raster = kwargs['input_array'].pop(0)
    river_raster = kwargs['input_array'].pop(0)
    input_rasters = kwargs['input_array']
    output_raster = kwargs['output_array'][0]

    # Determine no data value
    if data_type == '8_BIT_SIGNED':
        no_data_value = '-128'
    elif data_type == '8_BIT_UNSIGNED':
        no_data_value = '255'
    elif data_type == '16_BIT_SIGNED':
        no_data_value = '-32768'
    elif data_type == '16_BIT_UNSIGNED':
        no_data_value = '65535'
    else:
        no_data_value = -999
        print('\tERROR: Select a valid data type.')
        quit()

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

    # Calculate mean if calculate_mean is set to True
    if calculate_mean == True:
        mean_raster = CellStatistics(input_rasters, 'MEAN', 'DATA', 'SINGLE_BAND', '', 'AUTO_DETECT')
    else:
        mean_raster = Raster(input_rasters[0])

    # Set values to 0 for rivers and conditional statement
    print(f'\tCorrecting values to 0...')
    iteration_start = time.time()
    # Create conditional raster for sensitivity to pipelines and infrastructure
    correct_raster = Con(Raster(categorical_raster), 1, 0, conditional_statement)
    # Set values to 0 where rivers exists
    print('\t\tRemoving rivers...')
    raster_remove_1 = Con(Raster(river_raster) == 1, 0, mean_raster)
    # Set values to 0 for conditional statement
    print('\t\tRemoving non-vegetated areas...')
    raster_remove_2 = Con(correct_raster == 1, 0, raster_remove_1)
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
    # Replace null values with 0
    nonull_raster = Con(IsNull(raster_remove_2), 0, raster_remove_2)
    # Extract raster to study area
    extract_raster = ExtractByMask(nonull_raster, area_raster)
    # Export extracted raster
    arcpy.management.CopyRaster(extract_raster,
                                output_raster,
                                '',
                                '',
                                no_data_value,
                                'NONE',
                                'NONE',
                                data_type,
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # Create raster attribute table
    arcpy.management.BuildRasterAttributeTable(output_raster, 'Overwrite')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    out_process = f'Successfully post-processed continuous raster.'
    return out_process
