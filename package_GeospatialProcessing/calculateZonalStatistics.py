# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate zonal statistics
# Author: Timm Nawrocki
# Last Updated: 2022-01-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate zonal statistics" is a function that calculates zonal statistics of an input raster to a zone raster.
# ---------------------------------------------------------------------------

# Define a function to calculate zonal statistics
def calculate_zonal_statistics(**kwargs):
    """
    Description: calculates integer zonal statistics of an input raster to a zone raster
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
    from arcpy.sa import Raster
    from arcpy.sa import ZonalStatistics
    import datetime
    import time

    # Parse key word argument inputs
    statistic = kwargs['statistic']
    zone_field = kwargs['zone_field']
    work_geodatabase = kwargs['work_geodatabase']
    zone_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = zone_raster
    arcpy.env.extent = Raster(zone_raster).extent

    # Set output coordinate system
    arcpy.env.outputCoordinateSystem = Raster(zone_raster)

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(zone_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Determine input raster value type
    value_number = arcpy.management.GetRasterProperties(input_raster, "VALUETYPE").getOutput(0)
    no_data_value = arcpy.Describe(input_raster).noDataValue
    value_dictionary = {
        0: '1_BIT',
        1: '2_BIT',
        2: '4_BIT',
        3: '8_BIT_UNSIGNED',
        4: '8_BIT_SIGNED',
        5: '16_BIT_UNSIGNED',
        6: '16_BIT_SIGNED',
        7: '32_BIT_UNSIGNED',
        8: '32_BIT_SIGNED',
        9: '32_BIT_FLOAT',
        10: '64_BIT'
    }
    value_type = value_dictionary.get(int(value_number))
    print(f'\t\tOutput data type will be {value_type}.')
    print(f'\t\tOutput no data value will be {no_data_value}.')
    print('\t\t----------')

    # Calculate zonal statistics
    print(f'\t\tCalculating zonal {statistic.lower()}...')
    iteration_start = time.time()
    summary_raster = ZonalStatistics(zone_raster,
                                     zone_field,
                                     input_raster,
                                     statistic,
                                     'DATA',
                                     'CURRENT_SLICE',
                                     '',
                                     '')
    # Copy summary raster to output
    arcpy.management.CopyRaster(summary_raster,
                                output_raster,
                                '',
                                '',
                                no_data_value,
                                'NONE',
                                'NONE',
                                value_type,
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Return success message
    outprocess = f'\tSuccessfully created zonal {statistic.lower()}.'
    return outprocess
