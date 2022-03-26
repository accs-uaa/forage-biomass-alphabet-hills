# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Raster
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Extract Raster" is a function that extracts raster data to a mask.
# ---------------------------------------------------------------------------

# Define a function to extract raster data to a mask
def extract_raster(**kwargs):
    """
    Description: extracts a raster to a mask
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the area raster (must be first), target raster to extract (must be second), and mask raster (must be last)
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset
    Preconditions: the initial raster must be created from other scripts and the study area raster must be created manually
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    mask_raster = kwargs['input_array'][2]
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

    # Determine input raster value type
    value_number = arcpy.management.GetRasterProperties(input_raster, "VALUETYPE").getOutput(0)
    no_data_value = arcpy.Describe(input_raster + '/Band_1').noDataValue
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
    print(f'\tOutput data type will be {value_type}.')
    print(f'\tOutput no data value will be {no_data_value}.')
    print('\t----------')

    # Extract raster to study area
    print('\tPerforming extraction to mask raster...')
    iteration_start = time.time()
    extract_raster = ExtractByMask(input_raster, mask_raster)
    arcpy.management.CopyRaster(extract_raster,
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
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'\tSuccessfully extracted raster data to mask.'
    return out_process
