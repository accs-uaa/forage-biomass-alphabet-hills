# ---------------------------------------------------------------------------
# Calculate centroids
# Author: Amanda Droghini (adroghini@alaska.edu)
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate centroids" calculates the centroid for each geo-referenced raster. Geo-referenced rasters were created by manually centering and scaling aerial images from satellite imagery. The output is a CSV file that lists the file name and XY coordinates of each raster.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from arcpy.sa import *
import os

# Set root directory
drive = 'F:\\'
root_folder = 'ACCS_Work'

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/WildlifeEcology/Moose_AlphabetHills/Data')
imagery_folder = os.path.join(project_folder, 'Data_Input/imagery/aerial')
processed_folder = os.path.join(imagery_folder, 'processed/rgb')
temp_folder = os.path.join(imagery_folder, 'workspace')

# Define working geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')
arcpy.env.workspace = temp_folder

# Define the initial projection
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)

# Testing script with single image

# Define inputs
input_raster = os.path.join(processed_folder,"DSC_1942.tif")
file_name = "DSC_1942"

# Define outputs
output_con = os.path.join(temp_folder,''.join([file_name,'_con','.tif']))
output_polygon = os.path.join(temp_folder,''.join([file_name,'_poly','.shp']))
output_point = os.path.join(temp_folder,''.join([file_name,'_pt','.shp']))
output_point_project = os.path.join(temp_folder,''.join([file_name,'_pt','_proj','.shp']))
out_coor_system = arcpy.SpatialReference(4269)

# Convert a single-value raster
print("Creating single-value raster...")
con_raster = Con(input_raster, "1", "", "VALUE >= 0")
con_raster.save(output_con)

# Convert raster to polygon
print("Converting raster to polygon...")
arcpy.RasterToPolygon_conversion(output_con, output_polygon, "NO_SIMPLIFY")

# Feature to point
print("Converting polygon to point...")
arcpy.management.FeatureToPoint(output_polygon, output_point, "INSIDE")

# Project to NAD83
arcpy.management.Project(output_point, output_point_project, out_coor_system)

# Add coordinate fields
print("Adding coordinates...")
arcpy.AddXY_management(output_point_project)