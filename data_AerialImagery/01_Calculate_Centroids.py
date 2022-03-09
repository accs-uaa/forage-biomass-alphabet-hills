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
import glob

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

# Define workspace and geodatabase
work_geodatabase = os.path.join(project_folder, 'AlphabetHillsBrowseBiomass.gdb')
arcpy.env.workspace = temp_folder

# Define the initial projection
input_projection = 3338
initial_projection = arcpy.SpatialReference(input_projection)

# Define inputs
input_list = glob.glob(os.path.join(processed_folder, '*.tif'))

# Define global outputs
out_coor_system = arcpy.SpatialReference(4269)
all_centroids = os.path.join(work_geodatabase, "AerialImagery_Centroids")

for i in range(len(input_list)):

    input_raster = input_list[i]
    # Create file name by removing extension and select last part of string
    file_name = (os.path.splitext(input_raster)[0]).split('\\', -1)[-1]
    print('Processing ' + file_name + ', image ' + str(i+1) + ' of ' + str(len(input_list)))

    # Define outputs
    output_con = os.path.join(temp_folder, ''.join([file_name, '_con', '.tif']))
    output_polygon = os.path.join(temp_folder, ''.join([file_name, '_poly', '.shp']))
    output_point = os.path.join(temp_folder, ''.join([file_name, '_pt', '.shp']))
    output_point_project = os.path.join(temp_folder, ''.join([file_name, '_pt', '_proj', '.shp']))

    # Convert a single-value raster
    print("Creating single-value raster...")
    con_raster = Con(input_raster, "1", "", "VALUE >= 0")
    con_raster.save(output_con)

    # Convert raster to polygon
    print("Converting raster to polygon...")
    arcpy.RasterToPolygon_conversion(output_con, output_polygon, "NO_SIMPLIFY")

    # Feature to point
    print("Converting polygon to point...")
    arcpy.FeatureToPoint_management(output_polygon, output_point, "INSIDE")

    # Project to NAD83
    print("Changing projection...")
    arcpy.Project_management(output_point, output_point_project, out_coor_system)

    # Add coordinate fields
    print("Adding coordinates...")
    arcpy.AddXY_management(output_point_project)

    # Add file name as a field in the attribute table
    arcpy.CalculateField_management(output_point_project, field="Image_Name", expression='"' + file_name + '"', field_type="TEXT")

# List all centroid files
input_point_list = glob.glob(os.path.join(temp_folder, '*_pt_proj.shp'))

# Change workspace to write to gdb
arcpy.env.workspace = work_geodatabase

# Combine all projected centroids into a single shapefile
print ("Merging all centroids...")
arcpy.Merge_management(inputs=input_point_list, output=all_centroids)

# Remove extraneous fields
drop_fields = ["Id", "gridcode", "ORIG_FID"]
arcpy.DeleteField_management(all_centroids, drop_fields)