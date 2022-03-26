# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Reproject to integer raster and extract
# Author: Timm Nawrocki
# Last Updated: 2022-01-03
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Reproject to integer raster and extract" is a function that reprojects a raster and extracts to a study area.
# ---------------------------------------------------------------------------

# Define function to reproject raster and extract to study area
def reproject_extract(**kwargs):
    """
    Description: reprojects a raster and extracts to study area
    Inputs: 'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'conversion_factor' -- a number that will be multiplied with the original value before being converted to integer
            'input_array' -- an array containing the area raster and the input raster
            'output_array' -- an array containing the output raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    conversion_factor = kwargs['conversion_factor']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set snap raster
    arcpy.env.snapRaster = area_raster

    # Define the input and output coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    output_system = arcpy.SpatialReference(output_projection)

    # Project raster to output coordinate system
    print(f'\tReprojecting input raster...')
    iteration_start = time.time()
    # Define intermediate and output raster
    reprojected_raster = os.path.splitext(input_raster)[0] + '_reprojected.tif'
    # Define initial coordinate system
    arcpy.management.DefineProjection(input_raster, input_system)
    # Reproject raster
    arcpy.management.ProjectRaster(input_raster,
                                   reprojected_raster,
                                   output_system,
                                   'BILINEAR',
                                   cell_size,
                                   geographic_transformation,
                                   '',
                                   input_system)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Round to integer and extract to study area
    print(f'\tConverting raster to 32 bit integer...')
    iteration_start = time.time()
    integer_raster = Int((Raster(reprojected_raster) * conversion_factor) + 0.5)
    extract_raster = ExtractByMask(integer_raster, area_raster)
    arcpy.management.CopyRaster(extract_raster,
                                output_raster,
                                '',
                                '',
                                '-2147483648',
                                'NONE',
                                'NONE',
                                '32_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE')
    # Delete intermediate raster
    arcpy.management.Delete(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    out_process = 'Successful reprojecting and converting raster.'
    return out_process
