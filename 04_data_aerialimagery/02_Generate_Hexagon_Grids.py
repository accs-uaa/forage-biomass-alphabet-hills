# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Generate hexagon grid
# Author: Amanda Droghini (adroghini@alaska.edu)
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Generate hexagon grid" creates a hexagon tessellation that covers the extent of each geo-referenced image and a centroid within each hexagon. We'll use these outputs to manually create 6 x 12.5 m line transects within each hexagon to mirror the line-point intercept method that we use in the field.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
import glob

# Set root directory
drive = 'F:\\'
root_folder = 'ACCS_Work'

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
imagery_folder = os.path.join(project_folder, 'Data_Input/imagery/aerial')
workspace_folder = os.path.join(imagery_folder, 'workspace')

# Define workspace and geodatabase
survey_geodatabase = os.path.join(project_folder, 'AlphabetHills_Surveys.gdb')
arcpy.env.workspace = survey_geodatabase

# Define projection (NAD 83 / Alaska Albers)
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)
arcpy.env.outputCoordinateSystem = initial_projection

# Define inputs
polygon_list = glob.glob(os.path.join(workspace_folder, '*_poly.shp'))
hexagon_area = "405.95 SquareMeters"
# Area of a hexagon with a radius (center-to-vertex distance) of 12.5 m

for i in range(len(polygon_list)):

    input_polygon = polygon_list[i]
    # Create file name by removing extension and select last part of string
    file_name_temp = (os.path.splitext(input_polygon)[0]).split('\\', -1)[-1]
    file_name = os.path.splitext(file_name_temp)[0].split('_poly', -1)[0]
    print('Processing ' + file_name + ', image ' + str(i+1) + ' of ' + str(len(polygon_list)))

    # Define outputs
    output_hex_grid = os.path.join(survey_geodatabase, ''.join([file_name, '_Hex_Grid']))
    output_centroid = os.path.join(survey_geodatabase, ''.join([file_name, '_Hex_Centroids']))
    output_buffer = os.path.join(survey_geodatabase, ''.join([file_name, '_Hex_Buffers']))

    # Generate hexagon tessellation grid
    print("Creating hexagon grid...")
    arcpy.GenerateTessellation_management(output_hex_grid, Extent=input_polygon, Shape_Type="HEXAGON", Size=hexagon_area)

    # Generate centroid in every hexagon
    print("Generating centroids...")
    arcpy.FeatureToPoint_management(output_hex_grid, output_centroid, "INSIDE")

    # Create 2.4 meter buffer around centroid
    print("Generating buffers...")
    arcpy.analysis.PairwiseBuffer(output_centroid, output_buffer, buffer_distance_or_field="2.4 Meters",
                                  dissolve_option="NONE")
