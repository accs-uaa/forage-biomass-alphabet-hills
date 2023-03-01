# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Combine hexagonal centroids
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2022-10-28
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Combine hexagonal centroids" locates all plot center points based on distance from sampled points, combines center points into a single shapefile, re-projects it into GCS NAD 1983, and exports it to a comma-separated delimited file.
# ---------------------------------------------------------------------------

# Load modules
import arcpy
import os

# Set root directory
drive = 'F:\\'
root_folder = 'ACCS_Work\\Projects\\WildlifeEcology\\Moose_AlphabetHills'
data_folder = os.path.join(drive, root_folder, 'Data')

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

# Define parameters
field_img_name = "image_number"
field_plot_name = "plot_number"
field_type = "SHORT"

overlap_type = "WITHIN_A_DISTANCE"
search_distance = '5 Meters'
selection_type = "NEW_SELECTION"

# Define inputs
input_centroids = arcpy.ListFeatureClasses(wild_card="*_Centroids")
input_points = arcpy.ListFeatureClasses(wild_card="*_Points")

# Define outputs
output_plot_centers = os.path.join(geodatabase, "Surveyed_Centers")
output_project = os.path.join(geodatabase,"Surveyed_Centers_NAD83")
output_folder = os.path.join(data_folder, 'Data_Output', 'aerial_imagery_tables')
output_table = os.path.join(output_folder,"surveyed_plot_centers.csv")

# Create empty feature class in which to store a subset of centroids
# Define template based on any centroid shapefile
template = input_centroids[0]
arcpy.management.CreateFeatureclass(out_path=geodatabase,
                                    out_name="Surveyed_Centers",
                                    geometry_type="POINT",
                                    spatial_reference=initial_projection,
                                    template=template)
# Add field to establish relationships between image number, plot number, and center point
arcpy.management.AddField(output_plot_centers, field_name=field_img_name, field_type=field_type)
arcpy.management.AddField(output_plot_centers, field_name=field_plot_name, field_type=field_type)

# Iterate through each centroid file. Each file contains multiple centroids.
for i in range(len(input_centroids)):
    input_feature = input_centroids[i]

    print('Processing ' + input_feature + ', file ' + str(i + 1) + ' of ' + str(len(input_centroids)))

    # Add the name of the image as a field that can be queried later
    image_name = input_feature.split('_')[1]
    arcpy.management.AddField(input_feature, field_name=field_img_name, field_type=field_type)
    arcpy.management.CalculateField(input_feature, field=field_img_name, expression=image_name, expression_type="PYTHON3")

    # Select points that have the same image name as the centroid.
    relevant_points = [img for img in input_points if image_name in img]

    # Iterate over surveyed plots.
    for n in range(len(relevant_points)):
        select_feature = relevant_points[n]
        plot_number = int(select_feature.split("_")[2])

        print('Processing ' + select_feature)

        # Add field to establish relationship between plot number and centroid
        # Will be overwritten in the original file with each plot that is processed
        arcpy.management.AddField(input_feature, field_name=field_plot_name, field_type=field_type)
        arcpy.management.CalculateField(input_feature, field=field_plot_name, expression=plot_number)

        # Select centroid that is within 5 meters of surveyed points.
        relevant_centroids = arcpy.management.SelectLayerByLocation(input_feature, overlap_type=overlap_type,
                                                                    select_features=select_feature,
                                                                    search_distance=search_distance,
                                                                    selection_type=selection_type)

        # Add to plot center file
        arcpy.management.Append(relevant_centroids, output_plot_centers)

# Re-project plot center file to geographic coordinate system GCS NAD 1983
arcpy.management.Project(output_plot_centers, output_project, out_coor_system=output_projection)

# Add XY coordinates to each re-projected point
arcpy.management.AddXY(output_project)

# Export as comma-separated delimited file
arcpy.conversion.TableToTable(output_project, output_folder, output_table)