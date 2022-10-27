# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Export data from remote line-point intercepts
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2022-10-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Export data from remote line-point intercepts" extracts data from the line-point intercept files (point feature types) to a delimited csv file.
# ---------------------------------------------------------------------------

# Load modules
import arcpy
import os
import glob

# Set root directory
drive = 'F:\\'
root_folder = 'ACCS_Work\\Projects\\WildlifeEcology\\Moose_AlphabetHills'
data_folder = os.path.join(drive,root_folder,'Data')
output_folder = os.path.join(data_folder, 'Data_Output', 'image_tables')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define working geodatabase
geodatabase = os.path.join(data_folder, 'AlphabetHills_Surveys.gdb')
arcpy.env.workspace = geodatabase

# Define projection (NAD 83 / Alaska Albers)
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)

# Define inputs
input_list = arcpy.ListFeatureClasses(wild_card = "*_Points")

# Iterate through each points file and extract values as delimited file
for i in range(len(input_list)):
    input_table = input_list[i]

    # Define output
    output_table = os.path.join('.'.join([input_table, 'csv']))
    print('Processing ' + input_table + ', file ' + str(i + 1) + ' of ' + str(len(input_list)))

    arcpy.conversion.TableToTable(input_table, output_folder, output_table)