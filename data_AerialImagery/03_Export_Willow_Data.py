# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Export data from remote line-point intercepts
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2022-10-28
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Export data from remote line-point intercepts" extracts data from the line-point intercept files (point feature types) to a delimited csv file.
# ---------------------------------------------------------------------------

# Load modules
import arcpy
import os

# Set root directory
drive = 'F:\\'
root_folder = 'ACCS_Work\\Projects\\WildlifeEcology\\Moose_AlphabetHills'
data_folder = os.path.join(drive,root_folder,'Data')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define working geodatabase
geodatabase = os.path.join(data_folder, 'AlphabetHills_Surveys.gdb')
arcpy.env.workspace = geodatabase

# Define projections
# Input is NAD 83 / Alaska Albers
# Output is geographic GCS NAD 1983
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)
output_projection = 6318

# Define inputs
input_list = arcpy.ListFeatureClasses(wild_card = "*_Points")

# Define outputs
output_folder = os.path.join(data_folder, 'Data_Output', 'aerial_imagery_tables', 'survey_data')

# Iterate through each points file and extract values as delimited file
for i in range(len(input_list)):
    input_feature = input_list[i]

    # Define outputs
    output_feature = os.path.join(geodatabase, ''.join([input_feature, '_Project']))
    output_table = os.path.join('.'.join([input_feature, 'csv']))
    print('Processing ' + input_feature + ', file ' + str(i + 1) + ' of ' + str(len(input_list)))

    # Re-project to geographic coordinate system GCS NAD 1983
    arcpy.management.Project(input_feature, output_feature, out_coor_system=output_projection)

    # Add XY coordinates to each re-projected point
    arcpy.management.AddXY(output_feature)

    # Export as comma-separated delimited file
    arcpy.conversion.TableToTable(output_feature, output_folder, output_table)