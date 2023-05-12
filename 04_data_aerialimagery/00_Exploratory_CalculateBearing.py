# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate bearing angle between original and geo-referenced centroids
# Author: Amanda Droghini (adroghini@alaska.edu)
# Usage: Must be executed in a Python 3.9 installation.
# Description: This script creates lines from the original and geo-referenced coordinates, and uses those lines to calculate bearings. We'll compare this shift in direction to the "track" variable in the aircraft's metadata.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os

# Set root directory
drive = 'D:\\'
root_folder = 'ACCS_Work'

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
imagery_folder = os.path.join(project_folder, 'Data_Input/imagery/aerial')

# Define geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')

# Define projection (NAD 83 / Alaska Albers)
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)
arcpy.env.outputCoordinateSystem = initial_projection

# Define inputs
input_csv = os.path.join(imagery_folder, 'AerialImagery_Metadata_Subset.csv')
#input_csv = r"D:/ACCS_Work/Projects/WildlifeEcology/Moose_AlphabetHills/Data/Data_Input/imagery/aerial/AerialImagery_Metadata_Subset.csv"

# Define outputs
output_lines = os.path.join(work_geodatabase, "AerialImagery_Centroid_Lines")

# Convert points to lines
arcpy.XYToLine_management(input_csv, output_lines, "original_x", "original_y", "georef_x",
                          "georef_y", line_type="GEODESIC", id_field="rowid",attributes="ATTRIBUTES")

# Calculate bearing
arcpy.CalculateGeometryAttributes_management(in_features=output_lines,geometry_property=[["bearing", "LINE_BEARING"]])